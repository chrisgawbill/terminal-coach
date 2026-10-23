# Terminal Coach

Terminal Coach opens a real interactive shell on the left and a read-only,
contextual learning panel on the right. It uses Python's standard library and
tmux; it does not install Python packages.

From Terminal Coach's directory, run:

```sh
cd /home/chris_dev/projects/TerminalCoach
python3 -m terminal_coach
```

To start in another project, use `python3 -m terminal_coach --directory /path/to/project`.
Use the panel's up/down arrows (or `j`/`k`) to select a suggestion, Enter to
copy it into tmux's most recent buffer, and `q` to close the panel.
With tmux's default prefix, use Ctrl-b plus Left/Right to switch panes and
Ctrl-b then `]` to paste the selected command; press Enter yourself. Ctrl-b
then `d` detaches. Exiting the shell closes the session. The panel never sends
a command to the shell or executes it.

The panel refreshes cwd, Git status, branch, HEAD, latest commit time, and a
configured Docker container state. It reads no source file contents, shell
history, or terminal output; it reads project settings from `config/projects.json`.
Suggestions come from deterministic local rules, state their evidence, and explain their effects. A recent
commit is a clue only; it does not establish that a restart
or rebuild is needed. Project paths and commands live in `config/projects.json`.

Run the focused checks with:

```sh
python3 -m unittest discover -s tests -v
```
