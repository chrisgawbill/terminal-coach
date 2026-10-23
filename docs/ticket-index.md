# Tickets

## TERM-05 — Everyday context, help, and lifecycle

Status: ACTIVE. Approved: user requested useful non-Git everyday suggestions,
expanded help, a separate startup window, and restart/update/exit flags.
Scope: metadata-only everyday context; CLI and panel help; launch a separate
terminal window where a graphical terminal is available, with a terminal-only
fallback; `-restart`, `-update`, `-exit` and double-dash aliases. Updates are
explicit user actions and suggested shell commands are never executed.
Verify: context/rule and help coverage; lifecycle/window command checks;
Python suite and launcher tests; CLI help smoke; live tmux integration when
available. Human acceptance of desktop behavior and suggestions is pending.

States: IDEA, READY, ACTIVE, BLOCKED, DONE. Only human-authorized scope starts.

## TERM-01 — Contextual terminal learning panel

Status: ACTIVE. Approved: user requested a terminal with a right-side context
panel, matching existing architecture and documentation conventions; confirmed
native terminal on this server on 2026-10-23.

Scope: real shell on left; keyboard-usable panel on right; live cwd/Git/container
context; relevant, explained commands including configured Spotter dashboard
restart after a recent commit. Project-specific commands stay in configuration.
Select/copy commands for human execution; never auto-run them. Do not interrupt
partially typed input. Missing tools and non-repositories remain usable.

Verify:
- Pure rules cover recent commit + running container, dirty tree, no repository,
  stopped/missing container, and probe failure without misleading claims.
- Context follows cwd and detects a changed HEAD during a session.
- Terminal integration verifies pane launch, panel output, selection safeguards,
  literal copying without execution, and clean session exit.
- README launch command works and tests pass without installing Python packages.
- Human reviews the terminal and learning explanations before DONE.

Pending: human acceptance of the running terminal experience.

## TERM-02 — Launch from any directory

Status: ACTIVE. Approved: user requested `terminalCoach` from anywhere.
Scope: executable repository launcher linked onto the existing user PATH,
preserving cwd and forwarding CLI arguments. No shell configuration changes.
Verify: command resolves from another directory, `--help` works, cwd and
arguments reach the entry point unchanged, existing tests pass.
Pending: human acceptance of launch in an interactive terminal.

## TERM-03 — npm distribution and GitHub delivery

Status: ACTIVE. Approved: user requested push to chrisgawbill/terminal-coach and
npm/pnpm packaging. Scope: one package usable by both managers, portable CLI,
package installation verification, documentation, and GitHub delivery. Keep the
native Python/tmux runtime; document prerequisites. Local project configuration
must remain usable without shipping this server's absolute paths in the package.
Verify: package archive contents, isolated install and CLI smoke checks,
Python suite, CLI argument/cwd preservation, GitHub branch content verification.
Pending: registry publication/account availability and human terminal acceptance.

## TERM-04 — Useful outside a project

Status: ACTIVE. Approved: user requested the panel be useful when not in a
project. Scope: outside a Git repository, suggest general, explained navigation
and disk commands instead of only `pwd`; note a deleted cwd, home vs. elsewhere,
and whether Docker is installed. Context uses path metadata and PATH lookup only;
no directory listing, file contents, or project commands in core rules.
Verify: pure rules for home, non-home, deleted cwd, and Docker present/absent;
context reports home, missing cwd, and Docker availability; existing tests pass.
Pending: human acceptance of the suggestions in a live terminal.
