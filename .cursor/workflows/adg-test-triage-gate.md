---
description: Thin alias — ADG-backed test triage (/adg-test-triage-gate)
---

# /adg-test-triage-gate

**Tier:** Workflow alias only.

## Authority map

| Layer | SSOT |
|-------|------|
| Test accelerator invariant | [adg-test-accelerator-enforcement.mdc](../rules/adg-test-accelerator-enforcement.mdc) |
| Analysis procedures | [adg-analysis-procedures.mdc](../rules/adg-analysis-procedures.mdc) |
| ADG MCP | [adg-sqlite/SKILL.md](../skills/adg-sqlite/SKILL.md) |

## Invocation steps

1. `python tools/adg/adg_test_selector.py --from-diff` (or P7 `impacted_tests` when in top-20 accelerator).
2. Run scoped tests only; expand via ADG fanout if failures cluster.
3. Record evidence per [001-cursor-runtime-seam-execution.mdc](../rules/001-cursor-runtime-seam-execution.mdc).

⛔ Do not grep for dependency-based test selection.
