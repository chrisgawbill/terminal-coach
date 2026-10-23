# Working on Terminal Coach

Read README.md, docs/agent-development.md, then the selected ticket in
 docs/ticket-index.md. Read only relevant architecture sections and source files.

Keep the core project-agnostic: project commands belong in config/projects.json.
Separate context collection, pure suggestion rules, and terminal presentation.
Never execute a suggested command automatically. Do not read shell history,
credentials, file contents, or terminal output for context.
Branch names describe the work; no tool names in commits or code comments.
Run `python3 -m unittest discover -s tests -v` and ticket-specific checks.
Report checks that did not run. Human acceptance is required for DONE.
