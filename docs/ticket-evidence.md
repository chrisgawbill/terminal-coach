# Ticket evidence

## TERM-01 — 2026-10-23

Architecture review: Spotter AGENTS.md, README.md, ticket delivery contract, and
 dashboard/self-hosting command documentation; HockeyStatsWebApp AGENTS.md,
 agent-development.md, shared delivery contract, architecture boundaries, and
 frontend package scripts. Existing repositories were read without changes.

Applied conventions: project-agnostic core, configuration-owned project commands,
 one-directional layers, targeted documentation, compact scoped ticket, separate
 implementation worker, verification evidence, and explicit human acceptance.
 Native tmux replaces a browser frontend because the user confirmed a server
 terminal. Spotter's browser sweeps do not exercise native tmux panes.

Checks:
- Read-only context probes against Spotter, HockeyStatsWebApp/react, and /tmp
  found the correct repository roots and project check commands. Spotter Docker
  access was unavailable and appeared as a probe issue rather than a healthy
  container. No Docker restart or project test suggestion was executed.
- Live PTY launch attempted with isolated TMUX_TMPDIR. The environment rejected
  tmux Unix socket access with `Operation not permitted`. Live pane rendering,
  clipboard paste, cwd refresh, and session exit remain unverified here.
- Automated rule, context, launcher, and fake-screen checks: 11 passed.
  CLI `--help` and whitespace checks passed. These checks use mocked tmux and
  a fake curses screen and do not establish a live terminal pass.

Implementation review corrected POSIX command quoting, project-root matching,
checks launched from subfolders, automatic paste-buffer selection, layout bounds,
and startup failure reporting. Suggestions use local rules rather than a remote
model; source files and command history are not used as context.
Human acceptance: pending.
Remote handoff: no remote configured for this new repository; no push performed.

## TERM-02 — 2026-10-23

Installed executable `bin/terminalCoach` with a symlink in `~/.local/bin`,
which was already on PATH. The launcher resolves its checkout through the
symlink, sets module lookup, preserves cwd, and forwards arguments unchanged.

Verified `terminalCoach --help` from /tmp. A temporary interpreter stub verified
cwd preservation, module lookup, and an argument containing spaces. All 11
existing tests passed. Live tmux acceptance remains pending as in TERM-01.
Execution: single-agent. Context: targeted. Expansion: none.

## TERM-03 — 2026-10-23

Created npm package `@chrisgawbill/terminal-coach@0.1.0`; npm and pnpm share the
same archive. The Node launcher preserves cwd and arguments and reports a missing
Python interpreter. Package contents exclude tests, personal project paths, and
Python bytecode. Existing project commands were moved to user configuration.

Verification: `npm test` passed 2 launcher tests and 11 Python tests. Package
archive inspection and isolated offline npm installation passed; installed
`terminalCoach --help` runs from /tmp. pnpm 12.14 installation could not be verified: its store operation lock
failed with a read-only-filesystem error, including with isolated writable
XDG/store directories. This is a failed verification, not a compatibility pass. Live tmux remains unverified due the previously recorded socket
restriction. No registry publication was attempted.

Git CLI could not resolve github.com. The connected GitHub integration confirmed
a public chrisgawbill/terminal-coach repository with push access; final inspection found an initial MIT-license commit, which is preserved.
The package includes that license. Delivery uses the connected GitHub API. The local origin is configured.
The local feature branch retains its original commits; the remote receives the
reviewed source snapshot because Git transport is unavailable. See the handoff
for the verified remote commit. Registry release and live terminal acceptance
remain pending.
