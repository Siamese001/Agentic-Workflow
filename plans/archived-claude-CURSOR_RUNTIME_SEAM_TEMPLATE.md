---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\CURSOR_RUNTIME_SEAM_TEMPLATE.md'
original_relative_path: 'CURSOR_RUNTIME_SEAM_TEMPLATE.md'
source_sha256: f3a93e90cdd8c75eb3bc678c1cc74b457838529fa6c22c156f4baee37a9369f8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Cursor Runtime Seam Template

## Objective

Patch or verify exactly one runtime seam.

## Immutable constraints

- Do not edit `agentic_core` unless explicitly authorized.
- Do not change registries, v1 prompts, global gates, or broad runtime paths unless explicitly authorized.
- Do not mark PASS without completed commands and tests/gates.

## Allowed files

- `<path>`

## Commands

```bash
<exact command>
<exact test or gate>
```

## Required final response

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
FILES_CHANGED:
- [basename](repo/relative/path)
COMMANDS_RUN:
- command -> result
TESTS_GATES:
- command -> result
ARTIFACTS:
- [basename](repo/relative/path) or NONE
REPORTS_GENERATED: (when applicable)
- [basename](repo/relative/path)
NOTES:
- caveat
```

Use markdown hyperlinks for every path in receipt sections (chat + `*_receipt.md` + manifest `*_links` arrays).
