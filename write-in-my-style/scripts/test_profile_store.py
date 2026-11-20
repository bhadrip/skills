from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from io import StringIO
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from cryptography.fernet import Fernet

import profile_store


def fictional_profile(choice="ask_then_reason"):
    return {
        "version": 1,
        "rules": [
            {
                "channel": "slack",
                "audience": "teammate",
                "purpose": "request",
                "feature": "message_order",
                "choice": choice,
                "status": "observed",
            },
        ],
    }


class ProfileStoreTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "private" / "profile.sqlite3"
        self.keyring = Mock()
        self.keyring.get_password.return_value = None

        def save_key(service, account, key):
            self.keyring.get_password.return_value = key

        self.keyring.set_password.side_effect = save_key
        vault = patch.object(profile_store, "native_keyring", return_value=self.keyring)
        self.vault = vault.start()
        self.addCleanup(vault.stop)

    def test_absent_profile_needs_no_vault_or_files(self):
        self.assertEqual(profile_store.read_profile(self.path), {"revision": None, "profile": None})
        self.assertFalse(self.path.parent.exists())
        self.vault.assert_not_called()

    def test_round_trip_and_ciphertext_only(self):
        profile = fictional_profile()
        self.assertEqual(profile_store.save_profile(self.path, profile, None), {"revision": 1})
        self.assertEqual(profile_store.read_profile(self.path), {"revision": 1, "profile": profile})
        self.assertNotIn(b"ask_then_reason", self.path.read_bytes())
        with closing(sqlite3.connect(self.path)) as database:
            token = database.execute("SELECT token FROM profile").fetchone()[0]
        self.assertEqual(json.loads(Fernet(self.keyring.get_password.return_value).decrypt(token)), profile)

    def test_concurrent_first_save_keeps_a_single_key_and_profile(self):
        def attempt(choice):
            try:
                profile_store.save_profile(self.path, fictional_profile(choice), None)
            except profile_store.ProfileError as error:
                return choice, str(error)
            return choice, None

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, ("ask_then_reason", "context_then_point")))
        winners = [choice for choice, error in results if error is None]
        errors = [error for _, error in results if error is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("profile changed", errors[0])
        self.keyring.set_password.assert_called_once()
        self.assertEqual(profile_store.read_profile(self.path), {"revision": 1, "profile": fictional_profile(winners[0])})

    def test_failed_key_or_authentication_preserves_saved_profile(self):
        profile_store.save_profile(self.path, fictional_profile(), None)
        replacement = fictional_profile("context_then_point")
        key = self.keyring.get_password.return_value
        original = self.path.read_bytes()
        for invalid_key, message in ((None, "key is missing"), (Fernet.generate_key().decode(), "failed authentication")):
            with self.subTest(message=message):
                self.keyring.get_password.return_value = invalid_key
                with self.assertRaisesRegex(profile_store.ProfileError, message):
                    profile_store.save_profile(self.path, replacement, 1)
                self.assertEqual(self.path.read_bytes(), original)
        self.keyring.set_password.assert_called_once()
        self.keyring.get_password.return_value = key
        self.assertEqual(profile_store.save_profile(self.path, replacement, 1), {"revision": 2})
        self.assertEqual(profile_store.read_profile(self.path)["profile"], replacement)

    def test_locked_store_leaves_no_saved_profile(self):
        self.keyring.get_password.side_effect = RuntimeError("unavailable")
        with self.assertRaisesRegex(profile_store.ProfileError, "Unlock or enable"):
            profile_store.save_profile(self.path, fictional_profile(), None)
        self.assertIsNone(profile_store.read_profile(self.path)["profile"])
        self.assertNotIn(b"ask_then_reason", self.path.read_bytes())

    def test_conversation_text_and_identifiers_are_rejected_before_any_write(self):
        sample = "Fictional conversation text for this test."
        with_extra_fields = fictional_profile()
        with_extra_fields["rules"][0]["sample"] = sample
        with_named_audience = fictional_profile()
        with_named_audience["rules"][0]["audience"] = "Example Person"
        for invalid in (sample, with_extra_fields, with_named_audience, fictional_profile(sample)):
            with self.subTest(invalid=invalid):
                with self.assertRaises(profile_store.ProfileError) as result:
                    profile_store.save_profile(self.path, invalid, None)
                self.assertNotIn(sample, str(result.exception))
                self.assertFalse(self.path.parent.exists())
        self.vault.assert_not_called()

    def test_out_of_schema_ciphertext_is_never_returned(self):
        profile_store.save_profile(self.path, fictional_profile(), None)
        key = self.keyring.get_password.return_value
        invalid_payloads = (
            b'{"version":1,"rules":[],"sample":"Synthetic message."}',
            b'{"version":1,"rules":["Synthetic message."],"rules":[]}',
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                token = Fernet(key).encrypt(payload)
                with closing(sqlite3.connect(self.path)) as database, database:
                    database.execute("UPDATE profile SET token = ?", (token,))
                with self.assertRaisesRegex(profile_store.ProfileError, "style-only profile"):
                    profile_store.read_profile(self.path)

    def test_update_rejects_extra_and_duplicate_fields(self):
        invalid_inputs = (
            '{"revision":null,"profile":{},"sample":"Synthetic message."}',
            '{"revision":null,"profile":"Synthetic message.","profile":{}}',
        )
        for payload in invalid_inputs:
            with self.subTest(payload=payload):
                with self.assertRaises(profile_store.ProfileError) as result:
                    profile_store.read_update(StringIO(payload))
                self.assertNotIn("Synthetic message.", str(result.exception))


if __name__ == "__main__":
    unittest.main()
