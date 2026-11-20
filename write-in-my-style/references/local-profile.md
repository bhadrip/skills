# Local profile storage

A saved English voice profile contains only predefined style labels. For example, a profile can record that the user tends to put the request before the reason in Slack messages to teammates. The helper checks both saved and loaded data against the same allowlist. Generate illustrative examples from fresh fictional situations in the current session.

The helper stores one profile per OS user in `~/.write-in-my-style/profile.sqlite3`. It encrypts and authenticates the style labels with Fernet before SQLite receives them. The key is generated locally and held by macOS Keychain, Windows Credential Manager, or a Linux Secret Service such as GNOME Keyring. Enable and unlock the native credential store on the machine using the profile. [Fernet documentation](https://cryptography.io/en/latest/fernet/) · [Python keyring documentation](https://keyring.readthedocs.io/en/latest/)

Encryption covers the saved profile. The current assistant session can see the examples supplied to it and the style labels it loads. When calibration needs new examples, use fictional situations and invite the user to write them in their own words.

## Load and save

Run the commands from the skill directory. [uv](https://docs.astral.sh/uv/guides/scripts/) runs the helper with its declared Python dependencies.

```sh
uv run --script scripts/profile_store.py schema
uv run --script scripts/profile_store.py read
uv run --script scripts/profile_store.py save
```

- **Schema** lists the permitted version, scope fields, features, choices, and statuses. Use `any` only when the user confirmed a preference that broad. Use concrete scopes for observed rules. Keep tentative and unknown choices in the current session.
- **Read** returns JSON with `revision` and `profile`. Both are `null` when there is no saved profile.
- **Save** reads a JSON object with the same fields on standard input. Use the last-read revision and the complete updated profile. Use a JSON serializer and pass the payload as direct subprocess input. A successful save returns the new revision.

The following payload illustrates a first save with a fictional observation.

```json
{
  "revision": null,
  "profile": {
    "version": 1,
    "rules": [
      {
        "channel": "slack",
        "audience": "teammate",
        "purpose": "request",
        "feature": "message_order",
        "choice": "ask_then_reason",
        "status": "observed"
      }
    ]
  }
}
```

On a revision conflict, read again and apply the intended changes to the latest profile. On a credential or authentication failure, preserve the saved file and report the failure. Persistent storage requires the encrypted helper. An encrypted backup requires its matching credential-store key.
