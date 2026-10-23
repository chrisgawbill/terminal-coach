"""Small, evidence-based rules for explaining useful commands."""

from dataclasses import dataclass
import shlex

from .context import Snapshot, project_command, recent_commit


@dataclass(frozen=True)
class Suggestion:
    command: str
    reason: str
    explanation: str


def suggest(snapshot: Snapshot, now=None):
    result = []
    project = snapshot.project or {}
    if snapshot.dirty:
        result.append(Suggestion("git status --short", "The worktree has uncommitted changes.",
                                 "Shows changed paths without opening file contents."))
    if snapshot.git_root and snapshot.committed_at and recent_commit(snapshot, now):
        result.append(Suggestion("git show --stat --oneline HEAD", "HEAD was committed within the last 24 hours.",
                                 "Reviews the latest commit summary; recency alone does not mean a rebuild is needed."))
    if snapshot.container:
        if snapshot.container_state == "running":
            logs = project.get("logs", f"docker logs --tail 50 {shlex.quote(snapshot.container)}")
            result.append(Suggestion(logs,
                                     f"Docker reports {snapshot.container} is running.",
                                     "Reads the last 50 container log lines to help diagnose the running service."))
        elif snapshot.container_state in ("exited", "created", "paused", "restarting", "dead"):
            result.append(Suggestion(f"docker inspect {shlex.quote(snapshot.container)}",
                                     f"Docker reports container state: {snapshot.container_state}.",
                                     "Inspects container configuration and state; it does not change the container."))
            if snapshot.container_state == "exited" and project.get("restart"):
                result.append(Suggestion(project["restart"], "The configured container is stopped.",
                                         "Restarts the named container; its configured restart policy and application startup apply."))
        elif snapshot.container_state is None:
            result.append(Suggestion("docker ps -a", "The configured container state could not be read.",
                                     "Lists containers to diagnose Docker access or whether the configured container exists."))
    if snapshot.git_root and project.get("checks"):
        for command in project["checks"]:
            result.append(Suggestion(project_command(project, command), "This check is documented for the matched project.",
                                     "Runs the project's configured test command; it may take time and write test artifacts."))
    if snapshot.container_state == "running" and project.get("restart") and recent_commit(snapshot, now):
        result.append(Suggestion(project["restart"], "A recent commit and a running configured container are visible.",
                                 "Restarts the named container and may briefly interrupt service; a recent commit alone does not establish that a restart is needed."))
    if snapshot.git_root:
        result.append(Suggestion("git diff --stat", "Git is available for this repository.",
                                 "Summarizes tracked working-tree changes without displaying file contents."))
    if not result:
        result.append(Suggestion("pwd", "No repository-specific context is available.",
                                 "Prints the current directory; configure a project to get tailored checks."))
    return result
