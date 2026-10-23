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
    if not snapshot.git_root:
        result.extend(outside_repository(snapshot))
    if not result:
        result.append(Suggestion("pwd", "No repository-specific context is available.",
                                 "Prints the current directory; configure a project to get tailored checks."))
    return result


def outside_repository(snapshot: Snapshot):
    if not snapshot.cwd_exists:
        return [Suggestion("cd ..", "The shell's current directory no longer exists.",
                           "Moves to the parent directory; commands run in a deleted directory fail or behave oddly.")]
    result = [
        Suggestion("ls -lah", "This directory is not a Git repository.",
                   "Lists entries, including hidden ones (-a), with permissions, owner, and human-readable sizes (-h)."),
        Suggestion("pwd", "The shell is working in this directory.",
                   "Prints its absolute path, useful before copying paths or running commands."),
    ]
    tools = snapshot.available_tools
    if "du" in tools and "sort" in tools:
        result.append(Suggestion("du -h --max-depth=1 . | sort -h", "Disk use can be checked for this directory.",
                                 "Totals immediate subdirectory sizes, largest last; scanning large trees can take time."))
    if "df" in tools:
        result.append(Suggestion("df -h .", "This directory belongs to a filesystem.",
                                 "Shows that filesystem's used and available space in human-readable units."))
    if "find" in tools:
        result.append(Suggestion("find . -maxdepth 1 -type f -mtime -1", "find is available for this directory.",
                                 "Lists regular files modified in the last 24 hours at this level; does not open them."))
    if snapshot.location == "temporary":
        result.append(Suggestion("cd ~", "This path is in temporary storage.",
                                 "Returns home; temporary files may be removed by system cleanup, so keep lasting work elsewhere."))
    elif snapshot.location == "system" or not snapshot.cwd_writable:
        result.append(Suggestion("ls -ld .", "This is a system path or directory access reports it is not writable.",
                                 "Shows this directory's owner and permissions without changing them; use a personal folder for new work."))
    else:
        result.append(Suggestion("mkdir -p ./workspace", "This directory reports writable access.",
                                 "Creates a workspace subdirectory if absent; keeps existing contents. Use cd workspace to enter it."))
    if "ps" in tools:
        result.append(Suggestion("ps -u \"$USER\" -o pid,etime,comm", "ps is installed for checking your processes.",
                                 "Lists your processes with PID, elapsed time, and command name; does not stop them."))
    if "ss" in tools:
        result.append(Suggestion("ss -ltn", "ss is installed for inspecting network listeners.",
                                 "Lists listening TCP ports numerically; useful when checking a local service."))
    if not snapshot.at_home and snapshot.location != "temporary":
        result.append(Suggestion("cd ~", "The shell is outside your home directory.",
                                 "Returns to your home directory; `cd -` instead jumps back to the previous directory."))
    if snapshot.docker_available:
        result.append(Suggestion("docker ps", "Docker is installed on this machine.",
                                 "Lists running containers with their names, images, and ports; add -a to include stopped ones."))
    return result
