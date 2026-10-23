"""Curses side panel; a chosen command is copied, never sent to the shell."""

import argparse
import curses
import textwrap
import time

from .context import collect
from .suggestions import suggest


def tmux(args):
    import subprocess

    try:
        return subprocess.run(["tmux", *args], text=True, capture_output=True, timeout=2)
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args, 1, "", str(exc))


def draw(stdscr, target):
    curses.curs_set(0)
    stdscr.timeout(250)
    selected = 0
    message = "↑/↓ move · Enter copy · q close"
    snapshot = None
    items = []
    refresh_at = 0
    while True:
        now = time.monotonic()
        if snapshot is None or now >= refresh_at:
            previous = items[selected].command if items and 0 <= selected < len(items) else None
            path = tmux(["display-message", "-p", "-t", target, "#{pane_current_path}"])
            if path.returncode:
                return
            else:
                snapshot = collect(path.stdout.strip())
                items = suggest(snapshot)
                selected = next((i for i, item in enumerate(items) if item.command == previous),
                                min(selected, len(items) - 1))
                refresh_at = now + 3
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 8 or width < 28:
            lines = ["Terminal Coach", "Panel needs 28x8.", "Resize terminal or press q."]
            for y, line in enumerate(lines[:height]):
                stdscr.addnstr(y, 0, line, max(0, width - 1))
        else:
            stdscr.addnstr(0, 0, "TERMINAL COACH", width - 1, curses.A_BOLD)
            if snapshot:
                stdscr.addnstr(1, 0, snapshot.cwd, width - 1)
                if snapshot.git_root:
                    status = "dirty" if snapshot.dirty else ("clean" if snapshot.dirty is False else "Git status unavailable")
                    stdscr.addnstr(2, 0, f"Git {snapshot.branch or '(detached)'} · {status}", width - 1)
                    head_status = snapshot.head[:10] if snapshot.head else (
                        "no commits yet" if snapshot.has_commits is False else "unavailable")
                    stdscr.addnstr(3, 0, f"HEAD {head_status}", width - 1)
                else:
                    stdscr.addnstr(2, 0, "No Git repository", width - 1)
                if snapshot.container:
                    state = snapshot.container_state or "unavailable"
                    stdscr.addnstr(4, 0, f"Docker {snapshot.container}: {state}", width - 1)
                if height >= 16:
                    first_row = 6
                    slots = max(1, height - 15)
                    first_item = min(max(0, selected - slots + 1), max(0, len(items) - slots))
                    for index in range(first_item, min(len(items), first_item + slots)):
                        y = first_row + index - first_item
                        attr = curses.A_REVERSE if index == selected else curses.A_NORMAL
                        stdscr.addnstr(y, 0, items[index].command, width - 1, attr)
                    detail_y = height - 9
                    detail_lines = max(0, min(height - 2 - detail_y, height - 12))
                else:
                    detail_y = 5
                    detail_lines = max(0, height - 8)
                if items:
                    detail = items[selected]
                    if height < 16:
                        stdscr.addnstr(detail_y, 0, detail.command, width - 1, curses.A_REVERSE)
                        detail_y += 1
                        detail_lines = max(0, detail_lines - 1)
                    lines = textwrap.wrap(detail.reason, max(1, width - 4))
                    lines += textwrap.wrap(detail.explanation, max(1, width - 4))
                    for offset, line in enumerate(lines[:detail_lines]):
                        stdscr.addnstr(detail_y + offset, 2, line, width - 3)
                issue = snapshot.config_error or (snapshot.errors[0] if snapshot.errors else None)
                if issue and height >= 16:
                    stdscr.addnstr(5, 0, "Probe issue: " + issue, width - 1, curses.A_DIM)
            stdscr.addnstr(height - 2, 0, message, width - 1)
            stdscr.addnstr(height - 1, 0, "Ctrl-b ] paste · r refresh", width - 1)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), 27):
            return
        if key in (ord("r"), curses.KEY_RESIZE):
            snapshot = None
            continue
        if key in (curses.KEY_DOWN, ord("j")):
            selected = min(selected + 1, max(0, len(items) - 1))
        elif key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_ENTER, 10, 13) and items:
            result = tmux(["set-buffer", items[selected].command])
            message = ("Copied to the latest tmux buffer. Switch to shell and paste."
                       if result.returncode == 0 else "Could not copy command: " + result.stderr.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help=argparse.SUPPRESS)
    args = parser.parse_args()
    curses.wrapper(draw, args.target)


if __name__ == "__main__":
    main()
