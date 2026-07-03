---
name: "source-command-adg-test-triage-gate"
description: "Thin alias \u2014 ADG-backed test triage (/adg-test-triage-gate)"
---

# source-command-adg-test-triage-gate

Use this skill when the user asks to run the migrated source command `adg-test-triage-gate`.

## Command Template

# /adg-test-triage-gate

**Tier:** Workflow alias only.

## Authority map

| Layer | SSOT |
|-------|------|
| Test accelerator invariant | [adg-analysis-procedures.md](../rules/adg-analysis-procedures.md) |
| Analysis procedures | [adg-analysis-procedures.md](../rules/adg-analysis-procedures.md) |
| ADG MCP | [adg-sqlite/SKILL.md](../skills/adg-sqlite/SKILL.md) |

## Invocation steps

1. `python tools/adg/adg_test_selector.py --from-diff` (or P7 `impacted_tests` when in top-20 accelerator).
2. Run scoped tests only; expand via ADG fanout if failures cluster.
3. Record evidence per [001-runtime-seam-execution.md](../rules/001-runtime-seam-execution.md).

⛔ Do not grep for dependency-based test selection.

## MANUAL MIGRATION REQUIRED

Migrated from source command `adg-test-triage-gate` into a Codex skill. Invoke it as `$source-command-adg-test-triage-gate` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.
