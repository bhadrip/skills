"""Synthetic tests only; no photos, models, network, or external workspaces."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/portrait-to-print/scripts/project_log.py"
spec = importlib.util.spec_from_file_location("project_log", SCRIPT)
log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log)


class ProjectLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="portrait-log-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "private"

    def initialize(self):
        return log.init_workspace(self.path)

    def append(self, **changes):
        fields = dict(experiment_id="E001", hypothesis="A synthetic change may remove a seam.",
                      changed="Changed one synthetic parameter from 1 to 2.",
                      observed="The synthetic seam remained in two test views.",
                      decision="reject", stop_reason="No improvement; do not repeat this setting.")
        fields.update(changes)
        return log.append_experiment(self.path, **fields)

    def test_init_is_empty_private_and_copies_no_inputs(self):
        path = self.initialize()
        self.assertEqual(log.read_records(path), [])
        self.assertEqual(sorted(p.name for p in path.iterdir()), sorted([
            log.MARKER, log.JSONL, log.MARKDOWN, ".gitignore", "references", "candidates", "selected", "reports"]))
        for name in ("references", "candidates", "selected", "reports"):
            self.assertEqual(list((path / name).iterdir()), [])
        if os.name == "posix":
            self.assertEqual(path.stat().st_mode & 0o777, 0o700)
            self.assertEqual((path / log.JSONL).stat().st_mode & 0o777, 0o600)

    def test_accept_existing_empty_directory_only(self):
        self.path.mkdir()
        self.initialize()
        with self.assertRaisesRegex(ValueError, "nonempty"):
            self.initialize()

    def test_nonempty_target_is_preserved(self):
        self.path.mkdir()
        evidence = self.path / "unrelated.txt"
        evidence.write_text("preserve", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.initialize()
        self.assertEqual(evidence.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(len(list(self.path.iterdir())), 1)

    def test_workspace_rejects_git_tree_and_worktree_marker(self):
        for name, is_file in (("repository", False), ("worktree", True)):
            root = self.root / name
            root.mkdir()
            if is_file:
                (root / ".git").write_text("gitdir: synthetic", encoding="utf-8")
            else:
                (root / ".git").mkdir()
            with self.assertRaisesRegex(ValueError, "outside"):
                log.init_workspace(root / "private")
            self.assertFalse((root / "private").exists())

    def test_workspace_rejects_plugin_tree(self):
        plugin = self.root / "plugin"
        (plugin / ".codex-plugin").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "outside"):
            log.init_workspace(plugin / "private")

    @unittest.skipIf(os.name == "nt", "symlink creation may need extra Windows privileges")
    def test_workspace_rejects_symlink(self):
        target = self.root / "target"
        target.mkdir()
        self.path.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.initialize()
        self.assertEqual(list(target.iterdir()), [])

    def test_append_records_fields_hashes_and_prefixes(self):
        path = self.initialize()
        artifact = path / "reports/synthetic.txt"
        artifact.write_bytes(b"synthetic evidence only")
        first = self.append(artifacts=["reports/synthetic.txt"], source_sha256="A" * 64)
        old_json = (path / log.JSONL).read_bytes()
        old_md = (path / log.MARKDOWN).read_bytes()
        second = self.append(experiment_id="E002", parent="E001", decision="keep",
                             changed="Adjusted a different synthetic parameter.",
                             observed="Two synthetic checks now pass.", stop_reason="Bounded comparison complete.")
        self.assertTrue((path / log.JSONL).read_bytes().startswith(old_json))
        self.assertTrue((path / log.MARKDOWN).read_bytes().startswith(old_md))
        self.assertEqual(first["source_sha256"], "a" * 64)
        self.assertEqual(first["artifacts"][0]["sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest())
        self.assertEqual(second["previous_sha256"], first["record_sha256"])
        self.assertEqual(log.read_records(path), [first, second])

    def test_duplicate_id_unknown_parent_and_invalid_fields_do_not_append(self):
        path = self.initialize()
        self.append()
        original = (path / log.JSONL).read_bytes()
        for changes in ({}, {"experiment_id": "E002", "parent": "missing"},
                        {"experiment_id": "bad/id"}, {"observed": " "},
                        {"decision": "unknown"}, {"source_sha256": "invalid"},
                        {"stop_reason": "bad\x00value"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.append(**changes)
            self.assertEqual((path / log.JSONL).read_bytes(), original)

    def test_artifacts_require_existing_relative_files(self):
        path = self.initialize()
        outside = self.root / "outside.txt"
        outside.write_text("synthetic", encoding="utf-8")
        for value in (str(outside), "../outside.txt", "reports/missing.txt", "reports", "C:\\file.txt"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.append(artifacts=[value])
        self.assertEqual(log.read_records(path), [])

    @unittest.skipIf(os.name == "nt", "symlink creation may need extra Windows privileges")
    def test_artifact_and_log_symlinks_rejected(self):
        path = self.initialize()
        target = self.root / "synthetic.txt"
        target.write_text("outside", encoding="utf-8")
        (path / "reports/link.txt").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.append(artifacts=["reports/link.txt"])
        (path / log.JSONL).unlink()
        (path / log.JSONL).symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.append()
        self.assertEqual(target.read_text(encoding="utf-8"), "outside")

    def test_hash_tampering_and_markdown_drift_fail_closed(self):
        path = self.initialize()
        self.append()
        raw = (path / log.JSONL).read_text(encoding="utf-8")
        (path / log.JSONL).write_text(raw.replace("seam remained", "seam vanished"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "chain"):
            log.read_records(path)
        (path / log.JSONL).write_text(raw, encoding="utf-8")
        (path / log.MARKDOWN).write_text("altered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.append(experiment_id="E002")
        self.assertEqual((path / log.JSONL).read_text(encoding="utf-8"), raw)

    def test_partial_tail_and_lock_refuse_append(self):
        path = self.initialize()
        (path / log.JSONL).write_text('{"incomplete":', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "tail"):
            self.append()
        (path / log.JSONL).write_text("", encoding="utf-8")
        lock = path / ".experiment-log.lock"
        lock.write_text("synthetic writer", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "locked"):
            self.append()
        self.assertTrue(lock.exists())

    def test_malformed_record_and_marker_are_validation_errors(self):
        path = self.initialize()
        (path / log.JSONL).write_text("[]\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "schema"):
            self.append()
        (path / log.JSONL).write_text("", encoding="utf-8")
        (path / log.MARKER).write_text("[]\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "marker"):
            self.append()

    def test_script_repository_target_is_refused_without_writes(self):
        target = SCRIPT.parent / "must-not-create-test-workspace"
        self.assertFalse(target.exists())
        with self.assertRaisesRegex(ValueError, "outside"):
            log.init_workspace(target)
        self.assertFalse(target.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX permission check")
    def test_open_workspace_permissions_fail_closed(self):
        path = self.initialize()
        path.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "owner-only"):
            self.append()
        path.chmod(0o700)
        (path / log.JSONL).chmod(0o644)
        with self.assertRaisesRegex(ValueError, "owner-only"):
            self.append()

    def test_markdown_evidence_is_literal_not_executable_links(self):
        path = self.initialize()
        self.append(observed="![synthetic](https://invalid.example/test.png)\n## not a heading")
        text = (path / log.MARKDOWN).read_text(encoding="utf-8")
        self.assertIn("    ![synthetic]", text)
        self.assertIn("    ## not a heading", text)
        self.assertEqual(len(log.read_records(path)), 1)

    def test_cli_init_append_verify_and_invalid_input(self):
        def cli(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)
        result = cli("init", str(self.path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["inputs_copied"])
        result = cli("append", str(self.path), "--id", "E001", "--hypothesis", "Synthetic hypothesis",
                     "--changed", "Changed one synthetic setting", "--observed", "Synthetic check passed",
                     "--decision", "keep", "--stop-reason", "Bounded test complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = cli("verify", str(self.path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["verified_records"], 1)
        result = cli("append", str(self.path), "--id", "E002")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(log.read_records(self.path)), 1)


if __name__ == "__main__":
    unittest.main()
