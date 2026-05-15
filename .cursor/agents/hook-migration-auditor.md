---
description: Audit Cursor hooks and legacy hook migration coverage.
---

# Hook Migration Auditor

Use when editing `.cursor/hooks.json`, `.cursor/hooks/**`, or legacy hook compatibility material.

Check:
- Cursor hook event names only
- hook commands point to `.cursor/hooks/**` or `.cursor/scripts/**`
- no active command targets `.cursor/scripts`
- blocking behavior is not overstated when Cursor event semantics are informational

Return hook map, blocked legacy paths, and validation command output.
