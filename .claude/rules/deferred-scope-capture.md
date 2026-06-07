# DEPRECATED — deferred-scope capture superseded by native spawn_task (W4, ADR-096)

> ⛔ Retired W4 (`claude-native-supersession-9d3f7a`). The `DEFERRED_SCOPE:` marker → auto-score →
> capture-hook → Notion-post pipeline emulated a backlog-handoff mechanism Claude Code now provides
> natively.

## What to do instead

When you notice out-of-scope work, call the native **`spawn_task`** tool: it drops a background-task
chip the user can spin into its own session/worktree with one click, or dismiss. No marker, no scorer,
no recovery hook. A durable Notion backlog row remains available via explicit user action only.

Invariant SSOT: `.claude/rules/constitutional.md` §24.
