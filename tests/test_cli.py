import os
import subprocess
import unittest
from unittest.mock import patch

from terminal_coach import __main__ as cli


class CliTests(unittest.TestCase):
    def test_single_dash_help_does_not_launch(self):
        with patch("sys.argv", ["terminalCoach", "-help"]), \
                patch("sys.stdout") as output, patch.object(cli.subprocess, "run") as run:
            with self.assertRaises(SystemExit) as exit_status:
                cli.main()
        self.assertEqual(exit_status.exception.code, 0)
        run.assert_not_called()
        self.assertIn("-restart", "".join(call.args[0] for call in output.write.call_args_list))

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

    def test_exit_targets_exact_coach_session(self):
        with patch.object(cli.subprocess, "run") as run, \
                patch("sys.argv", ["terminalCoach", "-exit", "--session", "terminal-coach-test"]):
            self.assertEqual(cli.main(), 0)
        self.assertEqual(run.call_args.args[0], ["tmux", "kill-session", "-t", "=terminal-coach-test"])

    def test_update_is_explicit_and_returns_installer_failure(self):
        with patch.object(cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)) as run, \
                patch("sys.argv", ["terminalCoach", "-update"]):
            self.assertEqual(cli.main(), 7)
        self.assertEqual(run.call_args.args[0], ["npm", "install", "--global", "github:chrisgawbill/terminal-coach"])

    def test_restart_builds_replacement_before_closing_old_session(self):
        calls = []

        def run(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "%1\n" if "new-session" in args else "", "")

        with patch.object(cli.subprocess, "run", side_effect=run), patch.dict(os.environ, {}, clear=True), \
                patch("sys.argv", ["terminalCoach", "-restart", "--session", "terminal-coach-test"]):
            self.assertEqual(cli.main(), 0)
        self.assertEqual([call[1] for call in calls],
                         ["-V", "has-session", "new-session", "split-window", "select-pane", "kill-session", "attach-session"])
        self.assertEqual(calls[5][-1], "=terminal-coach-test")

    def test_multiple_sessions_require_selection(self):
        result = subprocess.CompletedProcess([], 0, "terminal-coach-one\nterminal-coach-two\n", "")
        with patch.object(cli.subprocess, "run", return_value=result), \
                patch.dict(os.environ, {}, clear=True), patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                cli.managed_session(cli.argparse.ArgumentParser())

    def test_window_launch_preserves_directory_and_clears_parent_tmux(self):
        with patch.dict(os.environ, {"DISPLAY": ":1", "TMUX": "parent", "TMUX_PANE": "%2"}, clear=True), \
                patch.object(cli.shutil, "which", return_value="/usr/bin/xterm"), \
                patch.object(cli.subprocess, "Popen") as launch:
            self.assertTrue(cli.open_window(cli.Path("/tmp")))
        self.assertIn("--inline", launch.call_args.args[0])
        self.assertEqual(launch.call_args.kwargs["cwd"], cli.Path("/tmp"))
        self.assertNotIn("TMUX", launch.call_args.kwargs["env"])


if __name__ == "__main__":
    unittest.main()
