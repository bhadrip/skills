#!/usr/bin/env python3
"""Local-only private workspaces and append-only portrait experiment logs.

No inputs are copied or uploaded. POSIX permissions are owner-only; on Windows,
check the workspace ACL separately. Hash chaining detects changes to existing
records, not deliberate rewriting of the entire history by someone with access.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MARKER = ".portrait-workspace.json"
JSONL = "experiments.jsonl"
MARKDOWN = "EXPERIMENTS.md"
HEADER = "# Portrait experiments\n\nPrivate local record. Review rejected experiments before repeating them.\n\n"
ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
DECISIONS = ("keep", "reject", "inconclusive")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def private_path(value):
    raw = Path(value).expanduser().absolute()
    if raw.is_symlink():
        raise ValueError("Workspace target must not be a symlink.")
    path = raw.resolve()
    script_roots = [p for p in Path(__file__).resolve().parents
                    if (p / ".git").exists() or (p / ".codex-plugin").exists()]
    for root in script_roots:
        if path == root or root in path.parents:
            raise ValueError("Workspace must be outside the plugin/repository tree.")
    if any((p / ".git").exists() or (p / ".codex-plugin").exists()
           for p in (path, *path.parents)):
        raise ValueError("Workspace must be outside every Git/plugin tree.")
    return path


def create_file(path, text):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as target:
        target.write(text)
        target.flush()
        os.fsync(target.fileno())


def init_workspace(value):
    path = private_path(value)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError("Refusing an existing nonempty target or non-directory.")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)
    for name in ("references", "candidates", "selected", "reports"):
        (path / name).mkdir(mode=0o700)
    create_file(path / MARKER, canonical({"kind": "portrait-to-print-private", "schema": 1,
                                         "created_utc": utc_now()}) + "\n")
    create_file(path / JSONL, "")
    create_file(path / MARKDOWN, HEADER)
    create_file(path / ".gitignore", "*\n")
    return path


def regular_private_file(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular, non-symlink log file: {path.name}")
    info = path.stat()
    if info.st_nlink != 1:
        raise ValueError(f"Refusing hard-linked log file: {path.name}")
    if os.name == "posix" and info.st_mode & 0o077:
        raise ValueError(f"Log file is not owner-only: {path.name}")


def workspace(value):
    path = private_path(value)
    if not path.is_dir():
        raise ValueError("Initialize this private workspace first.")
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise ValueError("Workspace permissions must be owner-only (0700).")
    for name in (MARKER, JSONL, MARKDOWN):
        regular_private_file(path / name)
    marker = json.loads((path / MARKER).read_text(encoding="utf-8"))
    if not isinstance(marker, dict) or marker.get("kind") != "portrait-to-print-private" or marker.get("schema") != 1:
        raise ValueError("Unrecognized workspace marker.")
    return path


@contextmanager
def lock(path):
    target = path / ".experiment-log.lock"
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("Log is locked. Check for an active writer; do not blindly remove the lock.") from exc
    try:
        os.close(descriptor)
        yield
    finally:
        target.unlink()


def text_field(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 16000:
        raise ValueError(f"{name} must contain 1–16000 characters of evidence.")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError(f"{name} contains control characters.")
    return value.strip()


def markdown_record(record):
    lines = [f"## {record['id']} — {record['decision']}", ""]
    for name in ("parent", "utc", "hypothesis", "changed", "observed", "decision", "stop_reason", "source_sha256"):
        value = record.get(name)
        if value is not None:
            lines += [name.replace("_", " ").capitalize() + ":", ""]
            lines += ["    " + line for line in str(value).expandtabs(4).splitlines()]
            lines += [""]
    lines += ["Artifacts (workspace-relative paths and SHA-256):", ""]
    lines += ["    " + canonical(a) for a in record["artifacts"]] or ["    None recorded."]
    lines += ["", "Record SHA-256:", "", "    " + record["record_sha256"], "", ""]
    return "\n".join(lines)


def read_records(path):
    raw = (path / JSONL).read_text(encoding="utf-8")
    if raw and not raw.endswith("\n"):
        raise ValueError("Incomplete JSONL tail. Preserve files and inspect before continuing.")
    records, ids, previous = [], set(), None
    for number, line in enumerate(raw.splitlines(), 1):
        record = json.loads(line)
        if not isinstance(record, dict) or record.get("schema") != 1:
            raise ValueError(f"Unrecognized experiment schema at record {number}.")
        claimed = record.get("record_sha256")
        body = {k: v for k, v in record.items() if k != "record_sha256"}
        if record.get("sequence") != number or record.get("previous_sha256") != previous or claimed != digest(body):
            raise ValueError(f"Experiment chain failed validation at record {number}.")
        if not isinstance(record.get("id"), str) or not ID_PATTERN.fullmatch(record["id"]) or record.get("decision") not in DECISIONS:
            raise ValueError(f"Invalid experiment ID/decision at record {number}.")
        for name in ("utc", "hypothesis", "changed", "observed", "stop_reason"):
            text_field(record.get(name), name)
        if not isinstance(record.get("artifacts"), list):
            raise ValueError(f"Invalid artifact list at record {number}.")
        if record.get("id") in ids or (record.get("parent") is not None and record["parent"] not in ids):
            raise ValueError(f"Duplicate ID or invalid parent at record {number}.")
        ids.add(record["id"])
        records.append(record)
        previous = claimed
    expected = HEADER + "".join(markdown_record(r) for r in records)
    if (path / MARKDOWN).read_text(encoding="utf-8") != expected:
        raise ValueError("JSONL/Markdown mismatch. Preserve both; do not append until investigated.")
    return records


def artifact_record(path, value):
    relative = PurePosixPath(value)
    if not value or "\\" in value or ":" in value or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Artifacts must use workspace-relative paths without traversal.")
    target = path.joinpath(*relative.parts)
    if any(p.is_symlink() for p in (target, *target.parents) if p != path and path in p.parents):
        raise ValueError("Artifact paths must not contain symlinks.")
    if not target.is_file():
        raise ValueError(f"Artifact must already exist as a file: {value}")
    return {"path": relative.as_posix(), "sha256": file_hash(target)}


def append_bytes(path, value):
    flags = os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "ab") as target:
        info = os.fstat(target.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Log file changed while acquiring the append handle.")
        target.write(value.encode("utf-8"))
        target.flush()
        os.fsync(target.fileno())


def append_experiment(value, *, experiment_id, parent=None, hypothesis, changed,
                      observed, decision, stop_reason, artifacts=(), source_sha256=None):
    if not isinstance(experiment_id, str) or not ID_PATTERN.fullmatch(experiment_id):
        raise ValueError("ID must start with a letter and contain 1–64 letters, digits, underscores or hyphens.")
    if decision not in DECISIONS:
        raise ValueError("Decision must be keep, reject, or inconclusive.")
    fields = {k: text_field(v, k) for k, v in dict(hypothesis=hypothesis, changed=changed,
              observed=observed, stop_reason=stop_reason).items()}
    if source_sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", source_sha256):
        raise ValueError("Source SHA-256 must be exactly 64 hexadecimal characters.")
    path = workspace(value)
    with lock(path):
        records = read_records(path)
        ids = {r["id"] for r in records}
        if experiment_id in ids:
            raise ValueError(f"Duplicate experiment ID: {experiment_id}")
        if parent is not None and parent not in ids:
            raise ValueError("Parent must name an existing experiment in this workspace.")
        evidence = [artifact_record(path, item) for item in artifacts]
        if len({a["path"] for a in evidence}) != len(evidence):
            raise ValueError("Duplicate artifact path.")
        body = dict(schema=1, sequence=len(records) + 1, id=experiment_id, parent=parent,
                    utc=utc_now(), **fields, decision=decision, artifacts=evidence,
                    source_sha256=source_sha256.lower() if source_sha256 else None,
                    previous_sha256=records[-1]["record_sha256"] if records else None)
        record = dict(body, record_sha256=digest(body))
        # Both are append-only. A crash between writes is detected on the next read;
        # never silently truncate or replace the JSONL authority to repair a mismatch.
        append_bytes(path / JSONL, canonical(record) + "\n")
        append_bytes(path / MARKDOWN, markdown_record(record))
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create an empty private workspace; copy no inputs.").add_argument("workspace")
    commands.add_parser("verify", help="Check hash chain and Markdown agreement.").add_argument("workspace")
    append = commands.add_parser("append", help="Append an evidence-based experiment outcome.")
    append.add_argument("workspace")
    append.add_argument("--id", dest="experiment_id", required=True)
    append.add_argument("--parent")
    for name in ("hypothesis", "changed", "observed", "stop-reason"):
        append.add_argument("--" + name, required=True)
    append.add_argument("--decision", choices=DECISIONS, required=True)
    append.add_argument("--artifact", dest="artifacts", action="append", default=[], help="Existing workspace-relative file; repeat as needed.")
    append.add_argument("--source-sha256")
    args = vars(parser.parse_args(argv))
    command, value = args.pop("command"), args.pop("workspace")
    try:
        if command == "init":
            result = {"workspace": str(init_workspace(value)), "inputs_copied": False}
        elif command == "verify":
            path = workspace(value)
            with lock(path):
                records = read_records(path)
            result = {"verified_records": len(records), "experiments": [
                {k: r[k] for k in ("id", "parent", "decision", "stop_reason")} for r in records]}
        else:
            result = append_experiment(value, **args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
