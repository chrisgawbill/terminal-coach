"""Start a real shell and a contextual curses panel in a tmux session."""

import argparse
import os
import shlex
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Open a shell with a contextual learning panel.")
    parser.add_argument("--directory", type=Path, default=Path.cwd(), help="shell starting directory (default: current directory)")
    args = parser.parse_args()
    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        parser.error(f"not a directory: {directory}")
    try:
        subprocess.run(["tmux", "-V"], check=True, capture_output=True, timeout=3)
    except (OSError, subprocess.SubprocessError) as exc:
        parser.error(f"tmux is required: {exc}")

    session = f"terminal-coach-{uuid.uuid4().hex[:10]}"
    target = None
    created = False
    try:
        result = subprocess.run(["tmux", "new-session", "-d", "-P", "-F", "#{pane_id}",
                                 "-s", session, "-c", str(directory)],
                                check=True, capture_output=True, text=True)
        created = True
        target = result.stdout.strip()
        if not target:
            raise RuntimeError("tmux did not report the shell pane")
        command = [sys.executable, "-m", "terminal_coach.panel", "--target", target]
        panel_cmd = f"PYTHONPATH={shlex.quote(str(ROOT))} {shlex.join(command)}"
        subprocess.run(["tmux", "split-window", "-h", "-p", "40", "-t", target,
                        "-c", str(directory), panel_cmd], check=True)
        subprocess.run(["tmux", "select-pane", "-t", target], check=True)
        if os.environ.get("TMUX"):
            subprocess.run(["tmux", "switch-client", "-t", session], check=True)
        else:
            subprocess.run(["tmux", "attach-session", "-t", session], check=True)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        if created:
            subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)
        print(f"Could not start Terminal Coach: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
