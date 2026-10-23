import unittest
from datetime import datetime, timezone, timedelta

from terminal_coach.context import Snapshot
from terminal_coach.suggestions import suggest


class SuggestionsTests(unittest.TestCase):
    def snapshot(self, **changes):
        values = dict(cwd="/repo", project=None, git_root="/repo", branch="main", dirty=False,
                      head="abc123", committed_at=datetime.now(timezone.utc), container=None,
                      container_state=None)
        values.update(changes)
        return Snapshot(**values)

    def test_recent_commit_and_running_container_suggest_documented_restart(self):
        project = {"path": "/repo", "container": "spotter-dashboard",
                   "restart": "docker restart spotter-dashboard",
                   "logs": "docker logs --tail 50 spotter-dashboard", "checks": ["npm test"]}
        items = suggest(self.snapshot(project=project, container="spotter-dashboard", container_state="running"))
        commands = [item.command for item in items]
        self.assertIn("docker restart spotter-dashboard", commands)
        restart = next(item for item in items if item.command.startswith("docker restart"))
        self.assertIn("does not establish", restart.explanation)

    def test_dirty_tree_and_stopped_container_are_evidence_specific(self):
        project = {"path": "/repo", "container": "svc", "restart": "docker restart svc"}
        items = suggest(self.snapshot(project=project, container="svc", container_state="exited", dirty=True))
        by_command = {item.command: item for item in items}
        self.assertIn("git status --short", by_command)
        self.assertIn("docker restart svc", by_command)
        self.assertIn("stopped", by_command["docker restart svc"].reason)

    def test_no_repo_and_unavailable_container_do_not_claim_healthy(self):
        no_repo = suggest(self.snapshot(git_root=None, branch=None, dirty=None, head=None,
                                        committed_at=None, project=None))
        self.assertEqual([item.command for item in no_repo], ["pwd"])
        project = {"path": "/repo", "container": "svc"}
        unavailable = suggest(self.snapshot(project=project, container="svc", container_state=None))
        self.assertIn("docker ps -a", [item.command for item in unavailable])
        self.assertFalse(any("running" in item.reason.lower() for item in unavailable))

    def test_old_commit_does_not_trigger_recent_commit_rule(self):
        old = datetime.now(timezone.utc) - timedelta(days=3)
        project = {"path": "/repo", "container": "svc", "restart": "docker restart svc"}
        items = suggest(self.snapshot(project=project, container="svc", container_state="running",
                                      committed_at=old))
        self.assertNotIn("docker restart svc", [item.command for item in items])


if __name__ == "__main__":
    unittest.main()
