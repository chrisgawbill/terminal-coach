"""Read-only collection of shell, Git, and configured container metadata."""

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "terminal-coach" / "projects.json"
CONFIG = Path(os.environ["TERMINAL_COACH_CONFIG"]) if os.environ.get("TERMINAL_COACH_CONFIG") else (
    USER_CONFIG if USER_CONFIG.exists() else ROOT / "config" / "projects.json"
)


@dataclass(frozen=True)
class Snapshot:
    cwd: str
    project: dict | None
    git_root: str | None
    branch: str | None
    dirty: bool | None
    head: str | None
    committed_at: datetime | None
    container: str | None
    container_state: str | None
    errors: tuple[str, ...] = ()
    config_error: str | None = None
    has_commits: bool | None = None


def _run(args, cwd=None):
    try:
        result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if result.returncode:
        return None, result.stderr.strip() or f"exit {result.returncode}"
    return result.stdout.strip(), None


def configured_project(git_root, config_path=CONFIG):
    if not git_root:
        return None, None
    try:
        config = json.loads(Path(config_path).read_text())
        if not isinstance(config, dict):
            raise ValueError("top level must be an object")
        projects = config.get("projects", [])
        if not isinstance(projects, list):
            raise ValueError("projects must be a list")
        for project in projects:
            if not isinstance(project, dict) or not isinstance(project.get("path"), str):
                raise ValueError("each project needs a path")
            if not project["path"] or "\n" in project["path"] or "\r" in project["path"]:
                raise ValueError("project paths must be non-empty and single line")
            root = Path(project["path"]).expanduser().resolve()
            if Path(git_root).resolve() == root:
                for key in ("container", "restart", "logs"):
                    if key in project and not isinstance(project[key], str):
                        raise ValueError(f"{key} must be a string")
                    if key in project and ("\n" in project[key] or "\r" in project[key]):
                        raise ValueError(f"{key} must be single line")
                    if key in project and key in ("container", "restart", "logs") and not project[key]:
                        raise ValueError(f"{key} must not be empty")
                if "checks" in project and (not isinstance(project["checks"], list)
                                            or not all(isinstance(check, str) and check for check in project["checks"])):
                    raise ValueError("checks must be a list of non-empty strings")
                if any("\n" in check or "\r" in check for check in project.get("checks", [])):
                    raise ValueError("checks must be single line")
                return project, None
        return None, None
    except (OSError, ValueError, TypeError) as exc:
        return None, f"Project config: {exc}"


def collect(cwd, config_path=CONFIG):
    cwd = str(Path(cwd).expanduser())
    errors = []
    git_root, error = _run(["git", "-C", cwd, "rev-parse", "--show-toplevel"])
    if error:
        errors.append(f"Git: {error}")
        git_root = None
    project, config_error = configured_project(git_root, config_path)

    branch = head = None
    dirty = None
    committed_at = None
    has_commits = None
    if git_root:
        branch, error = _run(["git", "-C", git_root, "branch", "--show-current"])
        if error:
            errors.append(f"Git branch: {error}")
        head, head_error = _run(["git", "-C", git_root, "rev-parse", "--verify", "HEAD"])
        if head:
            has_commits = True
        elif head_error and "Needed a single revision" in head_error:
            has_commits = False
        elif head_error:
            errors.append(f"Git HEAD: {head_error}")
        status, error = _run(["git", "-C", git_root, "status", "--porcelain"])
        if error:
            errors.append(f"Git status: {error}")
        else:
            dirty = bool(status)
        timestamp, error = _run(["git", "-C", git_root, "log", "-1", "--format=%cI"])
        if error and head:
            errors.append(f"Git commit time: {error}")
        elif timestamp:
            try:
                committed_at = datetime.fromisoformat(timestamp)
            except ValueError:
                errors.append("Git commit time: invalid timestamp")

    container = project.get("container") if project else None
    state = None
    if container:
        output, error = _run(["docker", "inspect", "--format", "{{.State.Status}}", container])
        if error:
            errors.append(f"Docker ({container}): {error}")
        else:
            state = output
    return Snapshot(cwd, project, git_root, branch, dirty, head, committed_at, container, state,
                    tuple(errors), config_error, has_commits)


def project_command(project, command):
    path = str(Path(project["path"]).expanduser().resolve())
    return f"cd {shlex.quote(path)} && {command}"


def recent_commit(snapshot, now=None):
    if snapshot.committed_at is None:
        return False
    now = now or datetime.now(timezone.utc)
    committed = snapshot.committed_at
    if committed.tzinfo is None:
        committed = committed.replace(tzinfo=timezone.utc)
    age = (now - committed.astimezone(timezone.utc)).total_seconds()
    return 0 <= age <= 24 * 60 * 60
