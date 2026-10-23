# Architecture

## Runtime

Native Linux terminal application: tmux provides a real shell pane and a right
side Python curses learning panel. Python standard library only; tmux is the
terminal multiplexer. No server, browser, API key, database, or model service.

## Boundaries

- `context.py`: read-only tmux pane metadata, Git status/latest commit, configured
  Docker container state. Subprocesses use argument lists and timeouts.
- `suggestions.py`: pure rules returning commands, reasons, and explanations.
- `panel.py`: curses rendering and keyboard selection; composed with context.
- `__main__.py`: launch/attach lifecycle and CLI.
- `config/projects.json`: project paths and known commands. No Spotter or Hockey
  project names in core modules. Match Git root, not folder basename.

Data flows context → suggestions → panel. A selection copies literal command text
to a new automatic tmux buffer; the human switches to the shell, pastes, and executes it.
The panel never sends keys to the shell or inspects its input line. Do not scrape terminal output
or history. Context stays in memory. External Git changes are detected on refresh;
recent commit means a timestamp within 24 hours and is described as evidence,
never proof that a restart or rebuild is required. A missing tool or failed probe
is shown as unavailable, never interpreted as healthy or clean.

## Scope

Rules cover a recent commit, dirty worktree, failed/missing probes, configured
container status, Git review and project checks. Suggestions explain flags and
side effects. No free-form inference or remote telemetry in the first version.
