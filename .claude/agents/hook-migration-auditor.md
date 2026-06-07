---
name: hook-migration-auditor
description: Audit Claude Code hooks and legacy hook migration coverage.
---

# Hook Migration Auditor

Use when editing `.claude/settings.json`, `.claude/hooks/**`, or legacy hook compatibility material.

Check:
- Claude Code hook event names only (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, …)
- hook commands point to `.claude/hooks/**` (governance backend under `.cursor/scripts/**` is the
  one allowed legacy dependency — see `.claude/hooks/lib/claude_hook_common.py`)
- hook bodies use the Claude Code I/O contract: block via exit code 2 (+ reason on stderr), not the
  old Cursor `{"decision": ...}` JSON
- blocking behavior is not overstated when an event is informational (e.g. `Stop` audits)

Return hook map, blocked legacy paths, and validation command output.
