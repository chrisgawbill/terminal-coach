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
        no_repo = suggest(self.no_repo())
        self.assertNotIn("git diff --stat", [item.command for item in no_repo])
        self.assertFalse(any("running" in item.reason.lower() for item in no_repo))
        project = {"path": "/repo", "container": "svc"}
        unavailable = suggest(self.snapshot(project=project, container="svc", container_state=None))
        self.assertIn("docker ps -a", [item.command for item in unavailable])
        self.assertFalse(any("running" in item.reason.lower() for item in unavailable))

    def no_repo(self, **changes):
        return self.snapshot(git_root=None, branch=None, dirty=None, head=None, committed_at=None, **changes)

    def test_outside_repository_suggests_general_navigation_and_disk_commands(self):
        commands = [item.command for item in suggest(self.no_repo(cwd="/srv", available_tools=("df",)))]
        self.assertIn("ls -lah", commands)
        self.assertIn("df -h .", commands)
        self.assertIn("cd ~", commands)
        self.assertNotIn("docker ps", commands)

    def test_outside_repository_at_home_with_docker(self):
        commands = [item.command for item in suggest(self.no_repo(cwd="/home/u", at_home=True,
                                                                  docker_available=True))]
        self.assertNotIn("cd ~", commands)
        self.assertIn("docker ps", commands)

    def test_everyday_tools_and_writable_directory(self):
        items = suggest(self.no_repo(cwd="/home/u/work", cwd_writable=True, location="home",
                                     available_tools=("df", "du", "sort", "find", "ps", "ss")))
        commands = [item.command for item in items]
        self.assertIn("mkdir -p ./workspace", commands)
        self.assertIn("ss -ltn", commands)
        self.assertIn('ps -u "$USER" -o pid,etime,comm', commands)
        self.assertIn("find . -maxdepth 1 -type f -mtime -1", commands)
        self.assertFalse(any(".git" in command for command in commands))

    def test_system_and_temporary_paths_have_specific_guidance(self):
        for location in ("system", "temporary"):
            items = suggest(self.no_repo(location=location, cwd_writable=True))
            commands = [item.command for item in items]
            self.assertNotIn("mkdir -p ./workspace", commands)
            self.assertIn("ls -ld ." if location == "system" else "cd ~", commands)
        self.assertFalse(any(item.command.startswith(("find ", "ss ", "ps ", "df "))
                             for item in suggest(self.no_repo())))

    def test_deleted_directory_only_suggests_leaving_it(self):
        items = suggest(self.no_repo(cwd_exists=False))
        self.assertEqual([item.command for item in items], ["cd .."])
        self.assertIn("no longer exists", items[0].reason)

    def test_old_commit_does_not_trigger_recent_commit_rule(self):
        old = datetime.now(timezone.utc) - timedelta(days=3)
        project = {"path": "/repo", "container": "svc", "restart": "docker restart svc"}
        items = suggest(self.snapshot(project=project, container="svc", container_state="running",
                                      committed_at=old))
        self.assertNotIn("docker restart svc", [item.command for item in items])


if __name__ == "__main__":
    unittest.main()
