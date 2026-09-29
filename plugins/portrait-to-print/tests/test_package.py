"""Public source-package checks; intentionally uses no portrait fixtures."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_manifests_are_synchronized(self):
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        legacy = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(portable["name"], ROOT.name)
        self.assertRegex(portable["version"], r"^\d+\.\d+\.\d+$")
        for field in ("name", "version", "description", "author", "license", "repository"):
            self.assertEqual(portable[field], legacy[field])
        interface = portable["extensions"]["com.openai"]["interface"]
        self.assertEqual(interface, legacy["interface"])
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in interface["defaultPrompt"]))
        self.assertNotIn("mcpServers", portable)
        self.assertNotIn("apps", portable)
        self.assertTrue((ROOT / legacy["skills"]).is_dir())

    def test_source_tree_is_text_only_and_contains_no_personal_payloads(self):
        allowed = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}
        special = {"LICENSE", ".gitignore"}
        patterns = [
            re.compile("/" + "Users" + r"/[A-Za-z0-9_.-]+/"),
            re.compile("/" + "home" + r"/[A-Za-z0-9_.-]+/"),
            re.compile(r"[A-Za-z]:\\" + "Users" + r"\\[^\\\s]+\\"),
            re.compile(r"IMG_\d{3,}"),
            re.compile(r"portrait_\d{8}_subject\d+"),
            re.compile(r"data:image/[^;]+;base64,"),
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        ]
        count = 0
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if any(part in {"__pycache__", ".pytest_cache", ".venv"} for part in relative.parts):
                continue  # development caches are ignored by git, never release inputs
            self.assertFalse(path.is_symlink(), str(relative))
            if not path.is_file():
                continue
            count += 1
            self.assertTrue(path.suffix in allowed or path.name in special, str(relative))
            payload = path.read_bytes()
            self.assertLess(len(payload), 150_000, str(relative))
            self.assertNotIn(b"\x00", payload, str(relative))
            text = payload.decode("utf-8")
            for pattern in patterns:
                self.assertIsNone(pattern.search(text), f"Potential private payload: {relative}")
        self.assertGreater(count, 10)

    def test_skill_references_and_code_are_present(self):
        skill = ROOT / "skills/portrait-to-print"
        entry = (skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(entry.startswith("---\nname: portrait-to-print\n"))
        for link in re.findall(r"\]\((references/[^)]+)\)", entry):
            target = (skill / link).resolve()
            self.assertTrue(target.is_relative_to(skill.resolve()))
            self.assertTrue(target.is_file(), link)
        for name in ("project_log.py", "mesh_tools.py", "blender_review.py"):
            self.assertTrue((skill / "scripts" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
