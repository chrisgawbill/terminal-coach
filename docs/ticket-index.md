# Tickets

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
