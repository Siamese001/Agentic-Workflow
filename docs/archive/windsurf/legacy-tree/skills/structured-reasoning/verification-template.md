# Structured Reasoning — Verification & Summary Template

Emit this block after Phase E (execution) completes.

> **MCP prefix note:** Tool names below use stable server-name style. Resolve the live numeric prefix from the tool list visible in your session.

```
## SR_SUMMARY
Task: <task title>
Date: <ISO timestamp>

What changed:
  - <file/artifact 1>: <what was done>
  - <file/artifact 2>: <what was done>

What was verified:
  - [ ] Scoped tests passed: <pytest command and result>
  - [ ] ADG health still OK: adg_health (server: adg_sqlite) — <result>
  - [ ] git diff reviewed — only expected files changed
  - [ ] Layer boundaries not violated
  - [ ] No new anti-patterns introduced

What remains uncertain:
  - <item> — <why uncertain, recommended follow-up>
  - NONE (if fully resolved)

Rollback / repair note:
  - Command: git reset --hard <baseline commit> (if destructive changes)
  - N/A (if no destructive changes)

Recommended next step:
  - <concrete action — who, what, when>

Task Manager update:
  - update_task (server: task_manager) status=done lessons_learned=<key insight>
```
