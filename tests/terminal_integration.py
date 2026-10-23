import os
import pty
import select
import subprocess
import tempfile
import time
from pathlib import Path
root = str(Path(__file__).resolve().parent.parent)
with tempfile.TemporaryDirectory(prefix='coach-live-') as tmp:
    env = dict(os.environ, TMUX_TMPDIR=tmp, TERM='xterm-256color', PYTHONPATH=root)
    env.pop('TMUX', None)
    def run(*args):
        return subprocess.run(args, env=env, capture_output=True, text=True, check=True).stdout.strip()
    children = []
    def launch(*args):
        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe('python3', ['python3', '-m', 'terminal_coach', '--inline', '--directory', '/tmp', *args], env)
        children.append((pid, fd))
        return fd
    def settle(fd):
        end = time.monotonic() + 2
        while time.monotonic() < end:
            if select.select([fd], [], [], .1)[0]:
                try: os.read(fd, 65536)
                except OSError: break
    try:
        fd = launch(); settle(fd)
        session = run('tmux', 'list-sessions', '-F', '#{session_name}')
        panes = run('tmux', 'list-panes', '-t', session, '-F', '#{pane_id}').splitlines()
        assert len(panes) == 2, panes
        panel = panes[1]
        output = run('tmux', 'capture-pane', '-p', '-t', panel)
        assert 'TERMINAL COACH' in output, output
        assert 'No Git repository' in output, output
        run('tmux', 'send-keys', '-t', panel, '?'); settle(fd)
        output = run('tmux', 'capture-pane', '-p', '-t', panel)
        assert 'HELP' in output.upper(), output
        run('tmux', 'send-keys', '-t', panel, 'q', 'Enter'); settle(fd)
        assert run('tmux', 'show-buffer') == 'ls -lah'
        replacement = launch('-restart', '--session', session); settle(replacement)
        new_session = run('tmux', 'list-sessions', '-F', '#{session_name}')
        assert new_session != session and '\n' not in new_session
        run('python3', '-m', 'terminal_coach', '-exit', '--session', new_session)
        print('PASS: live split, non-Git rendering, help, literal buffer copy, restart, exit')
    finally:
        subprocess.run(['tmux', 'kill-server'], env=env, capture_output=True)
        for pid, fd in children:
            os.close(fd)
            os.waitpid(pid, 0)
