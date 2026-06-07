---
description: Thin alias — Author-Gate before new anti-pattern / guardian debt (/antipattern-author-gate)
---

# /antipattern-author-gate

**Tier:** Workflow alias only.

## Authority map

| Layer | SSOT |
|-------|------|
| Tier 1 pipeline | [003-cursor-author-gate-hitl.md](../rules/003-cursor-author-gate-hitl.md) |
| Anti-pattern protocol | [author-gate-enforcement.md](../rules/author-gate-enforcement.md) § Anti-Pattern Author-Gate Extension |
| ADG detection | `ops_scripts/ci/_adg_burndown_gate.py`, [adg-p-band-burn-down-discipline.md](../rules/adg-p-band-burn-down-discipline.md) |

## Invocation steps

1. If ADG/burndown reports new violations → run full Author-Gate pipeline (`/author-gate-decision-gate`).
2. Use anti-pattern-specific options from `author-gate-enforcement.md` (Approve All / Reject All / Review Details).
3. On approve: guardian comments per pattern table; commit prefix `Author-Gate-APPROVED: <count> anti-pattern violations`.

⛔ No standalone scanner walkthrough in this file — use ADG gates + core pipeline.
