import os
import subprocess
import unittest
from unittest.mock import patch

from terminal_coach import __main__ as cli


class CliTests(unittest.TestCase):
    def test_launch_creates_split_then_attaches(self):
        calls = []

        def run(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "%1\n" if "new-session" in args else "", "")

        with patch.object(cli.subprocess, "run", side_effect=run), patch.dict(os.environ, {}, clear=True), \
                patch("sys.argv", ["terminal-coach"]):
            result = cli.main()
        self.assertEqual(result, 0)
        self.assertEqual([call[1] for call in calls], ["-V", "new-session", "split-window", "select-pane", "attach-session"])
        self.assertIn("terminal_coach.panel", calls[2][-1])
        self.assertIn("--target %1", calls[2][-1])
        self.assertEqual(calls[3][2:4], ["-t", calls[2][calls[2].index("-t") + 1]])

    def test_panel_command_failure_cleans_up_only_the_new_session(self):
        calls = []

        def run(args, **kwargs):
            calls.append(args)
            if args[1] == "new-session":
                return subprocess.CompletedProcess(args, 0, "%1\n", "")
            if args[1] == "split-window":
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0, "", "")

        with patch.object(cli.subprocess, "run", side_effect=run), patch.dict(os.environ, {}, clear=True), \
                patch("sys.argv", ["terminal-coach"]), patch("sys.stderr"):
            result = cli.main()
        self.assertEqual(result, 1)
        self.assertEqual(calls[-1][1], "kill-session")
        self.assertEqual(calls[-1][-1], calls[1][calls[1].index("-s") + 1])


if __name__ == "__main__":
    unittest.main()
