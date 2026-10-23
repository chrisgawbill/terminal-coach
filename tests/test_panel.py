import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from terminal_coach import panel


class FakeScreen:
    def __init__(self, height, width, keys=None):
        self.height = height
        self.width = width
        self.rows = {}
        self.keys = list(keys or [ord("q")])

    def timeout(self, _value):
        pass

    def erase(self):
        self.rows = {}

    def getmaxyx(self):
        return self.height, self.width

    def addnstr(self, y, x, value, count, _attr=0):
        if y < 0 or y >= self.height:
            raise AssertionError(f"row {y} outside {self.height}x{self.width}")
        self.rows[y] = str(value)[:count]

    def refresh(self):
        pass

    def getch(self):
        return self.keys.pop(0) if self.keys else ord("q")


class PanelTests(unittest.TestCase):
    def test_render_stays_inside_common_and_small_panel_sizes(self):
        snapshot = SimpleNamespace(cwd="/project", project=None, git_root="/project", branch="main",
                                   dirty=False, head="abcdef123456", has_commits=True,
                                   container=None, container_state=None, config_error=None, errors=())
        items = [SimpleNamespace(command=f"command {i}", reason="Evidence " * 8,
                                 explanation="A long explanation with useful context. " * 5)
                 for i in range(12)]
        for height, width in ((24, 32), (16, 28), (8, 28), (30, 80)):
            screen = FakeScreen(height, width)
            with self.subTest(size=(height, width)), patch.object(panel.curses, "curs_set"), \
                    patch.object(panel, "tmux", return_value=subprocess.CompletedProcess([], 0, "/project", "")), \
                    patch.object(panel, "collect", return_value=snapshot), patch.object(panel, "suggest", return_value=items):
                panel.draw(screen, "coach:0.0")
            if height >= 16:
                self.assertEqual(screen.rows[0], "TERMINAL COACH")

    def test_help_scrolls_and_enter_never_copies(self):
        snapshot = SimpleNamespace(cwd="/tmp", git_root=None, container=None,
                                   config_error=None, errors=())
        calls = []
        screen = FakeScreen(8, 28, [ord("?"), 10, panel.curses.KEY_END, ord("q"), ord("q")])
        def run(args):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "/tmp", "")
        with patch.object(panel.curses, "curs_set"), patch.object(panel, "tmux", side_effect=run), \
                patch.object(panel, "collect", return_value=snapshot), patch.object(panel, "suggest", return_value=[]):
            panel.draw(screen, "%1")
        self.assertFalse(any(call[0] == "set-buffer" for call in calls))
        text = " ".join(panel.HELP)
        for expected in ("-restart", "-update", "-exit", "credentials", "Page Down", "nothing runs automatically"):
            self.assertIn(expected, text)
        self.assertTrue(all(len(line) <= 27 for line in panel.help_lines(27)))

    def test_enter_copies_literal_to_latest_buffer_without_shell_input(self):
        snapshot = SimpleNamespace(cwd="/project", project=None, git_root=None, branch=None,
                                   dirty=None, head=None, has_commits=None, container=None,
                                   container_state=None, config_error=None, errors=())
        command = "printf '%s' 'literal text'"
        item = SimpleNamespace(command=command, reason="Evidence", explanation="Explanation")
        calls = []

        def run(args):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "/project", "") if len(calls) == 1 else \
                subprocess.CompletedProcess(args, 0, "", "")

        screen = FakeScreen(24, 32, [10, ord("q")])
        with patch.object(panel.curses, "curs_set"), patch.object(panel, "tmux", side_effect=run), \
                patch.object(panel, "collect", return_value=snapshot), patch.object(panel, "suggest", return_value=[item]):
            panel.draw(screen, "%1")
        set_buffer = next(call for call in calls if call[0] == "set-buffer")
        self.assertEqual(set_buffer[-1], command)
        self.assertNotIn("send-keys", set_buffer)
        self.assertNotIn("paste-buffer", set_buffer)
        self.assertNotIn("\n", set_buffer[-1])


if __name__ == "__main__":
    unittest.main()
