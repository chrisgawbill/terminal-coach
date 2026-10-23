"""Start a real shell and a contextual curses panel in a tmux session."""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "terminal-coach-"
UPDATE_URL = "https://github.com/chrisgawbill/terminal-coach/archive/refs/heads/main.tar.gz"


def managed_session(parser, requested=None):
    if requested:
        if not requested.startswith(PREFIX):
            parser.error("--session must name a Terminal Coach session")
        subprocess.run(["tmux", "has-session", "-t", f"={requested}"],
                       check=True, capture_output=True)
        return requested
    if os.environ.get("TMUX"):
        current = subprocess.run(["tmux", "display-message", "-p", "#{session_name}"],
                                 capture_output=True, text=True, check=True).stdout.strip()
        if current.startswith(PREFIX):
            return current
    result = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"],
                            capture_output=True, text=True)
    sessions = [name for name in result.stdout.splitlines() if name.startswith(PREFIX)]
    if len(sessions) != 1:
        parser.error("choose a running Coach session with --session NAME" if sessions
                     else "no running Terminal Coach session")
    return sessions[0]


def open_window(directory):
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    command = [sys.executable, "-m", "terminal_coach", "--inline", "--directory", str(directory)]
    for terminal, flags in (("x-terminal-emulator", ["-e"]), ("gnome-terminal", ["--"]),
                            ("konsole", ["-e"]), ("xterm", ["-e"])):
        executable = shutil.which(terminal)
        if executable:
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH")]))
            # A new terminal must attach its own client, even when launched inside tmux.
            env.pop("TMUX", None)
            env.pop("TMUX_PANE", None)
            subprocess.Popen([executable, *flags, *command], cwd=directory, env=env,
                             start_new_session=True)
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Open a real shell with a read-only contextual learning panel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  terminalCoach                         Open a separate terminal window if available
  terminalCoach --directory ~/Downloads Start in a chosen directory
  terminalCoach -restart                Replace the current/only Coach session
  terminalCoach -exit                   Close the current/only Coach session
  terminalCoach -update                 Update the global npm install from GitHub

Panel: arrows or j/k select, Enter copies, ? or h opens help, r refreshes,
q closes the panel. Ctrl-b Left/Right switches panes; Ctrl-b ] pastes.
You press Enter in the shell yourself. Ctrl-b d detaches; exit ends the shell.
Context: cwd/path metadata, Git metadata, available tools, configured Docker.
No shell history, file contents, or terminal output are collected.
Project commands: ~/.config/terminal-coach/projects.json (or TERMINAL_COACH_CONFIG).
Restart/exit close shells in the selected session; finish running work first.
Updates require network access and npm global-install permissions.""")
    parser.add_argument("-help", action="help", help="show this help message and exit")
    parser.add_argument("--directory", type=Path, default=Path.cwd(), help="shell starting directory")
    parser.add_argument("--inline", action="store_true", help="use this terminal instead of opening a window")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-restart", "--restart", action="store_true", help="replace current/only Coach session")
    actions.add_argument("-exit", "--exit", action="store_true", help="close current/only Coach session")
    actions.add_argument("-update", "--update", action="store_true", help="update global npm install from GitHub")
    parser.add_argument("--session", help="Coach tmux session to restart or exit")
    args = parser.parse_args()
    if args.session and not (args.restart or args.exit):
        parser.error("--session requires --restart or --exit")
    if args.update:
        command = ["npm", "install", "--global", UPDATE_URL]
        try:
            result = subprocess.run(command, check=False)
        except OSError as exc:
            print(f"Could not update Terminal Coach: {exc}", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"Terminal Coach update failed (npm exit {result.returncode}).\n"
                  "Check npm's error above for network or global-install permission problems.\n"
                  f"Retry directly: {shlex.join(command)}", file=sys.stderr)
        else:
            print("Terminal Coach updated. Start a new session to use the update.")
        return result.returncode
    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        parser.error(f"not a directory: {directory}")
    try:
        subprocess.run(["tmux", "-V"], check=True, capture_output=True, timeout=3)
    except (OSError, subprocess.SubprocessError) as exc:
        parser.error(f"tmux is required: {exc}")

    session = f"{PREFIX}{uuid.uuid4().hex[:10]}"
    created = False
    try:
        old_session = managed_session(parser, args.session) if args.restart or args.exit else None
        if args.exit:
            subprocess.run(["tmux", "kill-session", "-t", f"={old_session}"], check=True)
            return 0
        if not args.restart and not args.inline and open_window(directory):
            return 0
        result = subprocess.run(["tmux", "new-session", "-d", "-P", "-F", "#{pane_id}",
                                 "-s", session, "-c", str(directory)],
                                check=True, capture_output=True, text=True)
        created = True
        target = result.stdout.strip()
        if not target:
            raise RuntimeError("tmux did not report the shell pane")
        command = [sys.executable, "-m", "terminal_coach.panel", "--target", target]
        panel_cmd = f"PYTHONPATH={shlex.quote(str(ROOT))} {shlex.join(command)}"
        subprocess.run(["tmux", "split-window", "-h", "-l", "40%", "-t", target,
                        "-c", str(directory), panel_cmd], check=True)
        subprocess.run(["tmux", "select-pane", "-t", target], check=True)
        if old_session:
            # Move attached clients before closing their old shell.
            if os.environ.get("TMUX"):
                subprocess.run(["tmux", "switch-client", "-t", session], check=True)
            subprocess.run(["tmux", "kill-session", "-t", f"={old_session}"], check=True)
        if os.environ.get("TMUX"):
            if not old_session:
                subprocess.run(["tmux", "switch-client", "-t", session], check=True)
        else:
            subprocess.run(["tmux", "attach-session", "-t", session], check=True)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        if created:
            subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)
        print(f"Could not start Terminal Coach: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
