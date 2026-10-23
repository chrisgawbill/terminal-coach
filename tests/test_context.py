import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from terminal_coach.context import collect


class ContextTests(unittest.TestCase):
    def test_follows_cwd_to_git_root_and_detects_new_head(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            nested = root / "nested"
            nested.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "file.txt").write_text("one")
            subprocess.run(["git", "-C", str(root), "add", "file.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "one"], check=True)
            config = Path(temp) / "projects.json"
            config.write_text(json.dumps({"projects": [{"path": str(root), "checks": ["npm test"]}]}))
            first = collect(str(nested), config)
            (root / "file.txt").write_text("two")
            subprocess.run(["git", "-C", str(root), "commit", "-am", "two", "-q"], check=True)
            second = collect(str(nested), config)
            self.assertEqual(first.git_root, str(root))
            self.assertEqual(first.project["path"], str(root))
            self.assertNotEqual(first.head, second.head)
            self.assertFalse(second.dirty)

    def test_nested_repository_does_not_inherit_parent_project(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp) / "parent"
            nested = parent / "nested"
            nested.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(parent)], check=True)
            subprocess.run(["git", "init", "-q", str(nested)], check=True)
            config = Path(temp) / "projects.json"
            config.write_text(json.dumps({"projects": [{"path": str(parent), "checks": ["npm test"]}]}))
            snapshot = collect(str(nested), config)
            self.assertIsNone(snapshot.project)

    def test_unborn_repository_is_distinct_from_missing_git_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run(["git", "init", "-q", temp], check=True)
            snapshot = collect(temp, Path(temp) / "missing-config.json")
            self.assertEqual(snapshot.git_root, temp)
            self.assertFalse(snapshot.has_commits)
            self.assertFalse(snapshot.dirty)


if __name__ == "__main__":
    unittest.main()
