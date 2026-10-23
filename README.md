# Terminal Coach

Terminal Coach opens a real interactive shell on the left and a read-only,
contextual learning panel on the right. It requires Linux, Node.js 18 or newer,
Python 3.10 or newer, and tmux. The Python runtime uses only the standard
library; npm and pnpm install no dependencies.

Build the archive from a source checkout with `npm pack`. Install the resulting
`chrisgawbill-terminal-coach-0.1.0.tgz` with either package manager:

```sh
npm install --global ./chrisgawbill-terminal-coach-0.1.0.tgz
# or
pnpm add --global ./chrisgawbill-terminal-coach-0.1.0.tgz
```

The same package can be installed from GitHub:

```sh
npm install --global github:chrisgawbill/terminal-coach
# or
pnpm add --global github:chrisgawbill/terminal-coach
```

The package is not yet published to the npm registry. The owner can publish it
with `npm publish --access public` when ready. After installation, run
`terminalCoach` (or `terminal-coach`) from any directory. The shell starts in
your current directory; use `--directory /path/to/project` to choose another.
The launcher preserves the current directory and forwards all arguments to
Python. On a graphical Linux desktop, startup opens its own terminal window
(using x-terminal-emulator, gnome-terminal, konsole, or xterm). Without a display
or supported terminal, it uses the current terminal. Use `--inline` to request
that explicitly.

```sh
terminalCoach -restart   # replace the current or only running Coach session
terminalCoach -exit      # close the current or only running Coach session
terminalCoach -update    # update the global npm install from GitHub
terminalCoach -help      # all options, examples, controls, and context details
```

Double-dash forms (`--restart`, `--exit`, `--update`) also work; help accepts
`-help`, `--help`, or `-h`. When several
Coach sessions are running, use `--session terminal-coach-NAME` with restart or
exit to select one (session names are shown by `tmux list-sessions`). Restart
starts a fresh shell in the invoking directory or `--directory`; restart and
exit close shells in that session, so finish work first. Update explicitly runs
`npm install --global https://github.com/chrisgawbill/terminal-coach/archive/refs/heads/main.tar.gz`;
the HTTPS archive avoids requiring Git or GitHub SSH access. It needs network and
global-install permissions and does not restart existing sessions. For pnpm
managed installations, use `pnpm add --global github:chrisgawbill/terminal-coach`
instead. Source checkouts are not modified by `-update`.

If an older updater cannot download the update, run the HTTPS install command
above directly. A failed update reports npm's exit status and a retry command;
check npm's error for network or install-permission details. To save the error
when copying terminal text is difficult, run `terminalCoach -update > ~/terminal-coach-update.log 2>&1`.

Project commands are configured in `~/.config/terminal-coach/projects.json`.
The default config is an empty sample. Add project entries with an absolute
`path` and optional `container`, `checks`, `restart`, and `logs` fields, for
example:

```json
{
  "projects": [
    {
      "path": "/path/to/project",
      "checks": ["npm test"]
    }
  ]
}
```

Set `TERMINAL_COACH_CONFIG` to use a
different config file; when unset, the app uses `$XDG_CONFIG_HOME/terminal-coach/projects.json`
or `~/.config/terminal-coach/projects.json` if it exists.

Use the panel's up/down arrows (or `j`/`k`) to select a suggestion, Enter to
copy it into tmux's most recent buffer, and `q` to close the panel. Press `?`
or `h` for scrollable help covering controls, context, privacy, and lifecycle
commands; arrows and Page Up/Down scroll, and `q` returns to suggestions. With tmux's
default prefix, use Ctrl-b plus Left/Right to switch panes and Ctrl-b then `]`
to paste the selected command; press Enter yourself. Ctrl-b then `d` detaches.
Exiting the shell closes the session. The panel never sends a command to the
shell or executes it.

The panel refreshes cwd, Git status, branch, HEAD, latest commit time, and a
configured Docker container state. It reads no source file contents, shell
history, or terminal output. Suggestions come from deterministic local rules,
state their evidence, and explain their effects. Outside a Git repository the
panel suggests everyday navigation, recently modified file searches, directory
sizes, free space, processes, listening ports, and workspace creation. It adapts
to writable, home, temporary, and system paths and available tools, and points
you out of a directory that was deleted. This context uses path metadata and
PATH lookup; it does not list or open files. Suggested commands only run after
you paste and execute them.

Run the checks from a source checkout with `npm test` or
`python3 -m unittest discover -s tests -v`.

Run live PTY/tmux integration with `python3 tests/terminal_integration.py`.
It uses an isolated tmux server to check launch, non-Git rendering, help,
literal command copying, restart, and exit. Desktop window review requires a
graphical session.
