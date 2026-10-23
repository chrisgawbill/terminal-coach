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
Python.

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
copy it into tmux's most recent buffer, and `q` to close the panel. With tmux's
default prefix, use Ctrl-b plus Left/Right to switch panes and Ctrl-b then `]`
to paste the selected command; press Enter yourself. Ctrl-b then `d` detaches.
Exiting the shell closes the session. The panel never sends a command to the
shell or executes it.

The panel refreshes cwd, Git status, branch, HEAD, latest commit time, and a
configured Docker container state. It reads no source file contents, shell
history, or terminal output. Suggestions come from deterministic local rules,
state their evidence, and explain their effects.

Run the checks from a source checkout with `npm test` or
`python3 -m unittest discover -s tests -v`.
