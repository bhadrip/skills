# /// script
# requires-python = ">=3.10"
# dependencies = ["cryptography>=44,<52", "keyring>=25.6,<26"]
# ///

"""Store one encrypted writing profile in the local OS user account."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys

from cryptography.fernet import Fernet, InvalidToken

import profile_coverage
import profile_schema


SERVICE = "write-in-my-style"
ACCOUNT = "profile-key-v1"


class ProfileError(Exception):
    """An error that can be shown without exposing profile data."""


def native_keyring():
    # Select the OS backend directly so third-party plaintext backends cannot be used.
    if sys.platform == "darwin":
        from keyring.backends.macOS import Keyring

        return Keyring()
    if sys.platform == "win32":
        from keyring.backends.Windows import WinVaultKeyring

        ring = WinVaultKeyring()
        ring.persist = "local machine"
        return ring
    if sys.platform.startswith("linux"):
        from keyring.backends.SecretService import Keyring

        return Keyring()
    raise ProfileError("This OS has no supported local credential store.")


def profile_cipher(create):
    try:
        ring = native_keyring()
        key = ring.get_password(SERVICE, ACCOUNT)
        if key is None and create:
            key = Fernet.generate_key().decode("ascii")
            ring.set_password(SERVICE, ACCOUNT, key)
    except ProfileError:
        raise
    except Exception:
        raise ProfileError("Unlock or enable the local OS credential store and retry.") from None

    if key is None:
        raise ProfileError("The profile key is missing. Restore it from the original credential store.")
    try:
        return Fernet(key.encode("ascii"))
    except ValueError:
        raise ProfileError("The saved profile key is invalid.") from None


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON fields are unsupported.")
    return result


def decrypt(cipher, token):
    try:
        plaintext = cipher.decrypt(token)
    except (InvalidToken, TypeError):
        raise ProfileError("The profile failed authentication. Check the key and ciphertext.") from None
    try:
        profile = json.loads(plaintext, object_pairs_hook=unique_object)
        profile_schema.validate(profile)
    except ValueError:
        raise ProfileError("The saved data does not match the style-only profile format.") from None
    return profile


def check_path(path):
    if path.parent.is_symlink() or path.is_symlink():
        raise ProfileError("Use the real profile directory and database in your home directory.")


def read_profile(path):
    check_path(path)
    if not path.exists():
        return {"revision": None, "profile": None}

    # Allow SQLite to recover an interrupted write while opening an existing database only.
    with closing(sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)) as database:
        table = database.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'profile'"
        ).fetchone()
        record = None
        if table:
            record = database.execute("SELECT revision, token FROM profile WHERE id = 1").fetchone()

    if record is None:
        return {"revision": None, "profile": None}
    revision, token = record
    return {"revision": revision, "profile": decrypt(profile_cipher(create=False), token)}


def save_profile(path, profile, expected_revision):
    try:
        profile_schema.validate(profile)
    except ValueError as error:
        raise ProfileError(str(error)) from None
    payload = json.dumps(profile, sort_keys=True, separators=(",", ":")).encode("utf-8")

    check_path(path)
    path.parent.mkdir(mode=0o700, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=10)) as database, database:
        database.execute("BEGIN IMMEDIATE")
        database.execute(
            "CREATE TABLE IF NOT EXISTS profile ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), revision INTEGER NOT NULL, token BLOB NOT NULL)"
        )
        record = database.execute("SELECT revision, token FROM profile WHERE id = 1").fetchone()
        revision = record[0] if record else None
        if revision != expected_revision:
            raise ProfileError("The profile changed. Read the latest revision and reapply your update.")

        cipher = profile_cipher(create=record is None)
        if record:
            decrypt(cipher, record[1])
        token = cipher.encrypt(payload)
        next_revision = (revision or 0) + 1
        database.execute(
            "INSERT INTO profile (id, revision, token) VALUES (1, ?, ?) "
            "ON CONFLICT (id) DO UPDATE SET revision = excluded.revision, token = excluded.token",
            (next_revision, token),
        )
    return {"revision": next_revision}


def read_update(stream):
    try:
        update = json.load(stream, object_pairs_hook=unique_object)
    except ValueError:
        raise ProfileError("Pass a JSON object with revision and profile on stdin.") from None
    if not isinstance(update, dict) or update.keys() != {"revision", "profile"}:
        raise ProfileError("Pass only revision and profile in the update.")
    revision = update["revision"]
    if revision is not None and (type(revision) is not int or revision < 1):
        raise ProfileError("Use the revision returned by read, or null for a new profile.")
    return revision, update["profile"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("schema", help="show the allowed style labels")
    commands.add_parser("read", help="read the saved profile")
    commands.add_parser("save", help="save a style-only profile from standard input")
    coverage = commands.add_parser("coverage", help="compare style evidence for specific situations")
    coverage.add_argument("--scope", nargs=3, action="append", required=True, metavar=("CHANNEL", "AUDIENCE", "PURPOSE"))
    coverage.add_argument("--feature", action="append", choices=profile_schema.CHOICES)
    coverage.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    path = Path.home() / ".write-in-my-style" / "profile.sqlite3"

    try:
        if args.command == "schema":
            result = profile_schema.schema()
        elif args.command == "read":
            result = read_profile(path)
        elif args.command == "coverage":
            try:
                scopes = [profile_coverage.validate_scope(values) for values in args.scope]
            except ValueError as error:
                raise ProfileError(str(error)) from None
            features = args.feature or profile_schema.CHOICES
            report = profile_coverage.build_report(read_profile(path), scopes, features)
            if args.format == "markdown":
                print(profile_coverage.format_markdown(report))
                return 0
            result = report
        else:
            revision, profile = read_update(sys.stdin)
            result = save_profile(path, profile, revision)
    except ProfileError as error:
        print(error, file=sys.stderr)
        return 1
    except (OSError, sqlite3.Error, UnicodeError):
        print("Could not access the local profile. Check the profile directory and retry.", file=sys.stderr)
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
