# Structured Reasoning - Verification & Summary Template

Use this after approved execution completes.

```
Task: <task title>
Date: <ISO timestamp>

What changed:
  - <file/artifact 1>: <what was done>
  - <file/artifact 2>: <what was done>

What was verified:
  - [ ] Scoped tests passed: <command and result>
  - [ ] ADG health or relevant fallback checked: <result>
  - [ ] git diff reviewed; only expected files changed
  - [ ] Layer boundaries not violated
  - [ ] No new anti-patterns introduced

What remains uncertain:
  - <item>: <why uncertain, recommended follow-up>
  - NONE (if fully resolved)

Rollback / repair note:
  - Command: <git restore/revert command>
  - N/A (if no special rollback is needed)

Recommended next step:
  - <concrete action, or NONE>
```
