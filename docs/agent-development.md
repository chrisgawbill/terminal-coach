# Development workflow

The human is Product Owner. Work only inside the approved request. Record scope,
acceptance, and unresolved decisions in a compact ticket before implementation.
Use targeted reads, expand only for an unresolved dependency. The coordinator
owns scope and evidence review; delegate substantial implementation to a bounded
coder. Keep ordinary localized changes single-agent. Review for readable names,
small functions, clear boundaries, and unnecessary abstractions before delivery.

Use feature branches. Run unit and terminal integration checks; browser-only
Spotter sweeps do not apply to this native terminal application. Keep evidence in
docs/ticket-evidence.md and instructions in README.md. DONE requires the ticket's
Verify list and Product Owner acceptance. Report actual execution mode, context
scope, failed/skipped checks, and pending acceptance. Never infer acceptance.
