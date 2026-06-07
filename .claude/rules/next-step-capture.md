# DEPRECATED — next-step capture superseded by native spawn_task (W4, ADR-096)

> ⛔ Retired W4 (`claude-native-supersession-9d3f7a`). The `NEXT_STEP:` marker → capture-hook pipeline
> is superseded by native **`spawn_task`** background-task chips.

## What to do instead

Surface a follow-up via `spawn_task` (background-task chip) rather than a `NEXT_STEP:` marker. For
scoped wave-deferral inside an active plan, note it in the plan body. No marker, no hook.

Invariant SSOT: `.claude/rules/constitutional.md` §24.
