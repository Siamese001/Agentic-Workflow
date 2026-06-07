---
trigger: model_decision
description: Use this rule for the SVP recommendation lens (1st-5th priorities) and the Red/Yellow/Green Author-Gate calibration metrics. Trigger doctrine + scoring + format live in author-gate-decision-points.md and author-gate-enforcement.md.
---

# Author-Gate SVP Calibration — Unique-Content Stub

> Packet shape SSOT: `.windsurf/schemas/author_gate_packet.schema.json` (plan `author-gate-ssot-consolidation-b7c3e1`). This file owns the **SVP recommendation lens** + **R/Y/G calibration metrics**; trigger taxonomy in `author-gate-decision-points.md`; scoring/marker mechanics in `author-gate-enforcement.md`.

> Trimmed 2026-05-01: trigger taxonomy moved to `author-gate-decision-points.md`; scoring parameters and packet format moved to `author-gate-enforcement.md`. This file retains only the SVP-recommendation lens and the calibration metrics that exist nowhere else.

## SVP Recommendation Priority Lens

When ranking Author-Gate options, the ⭐ Recommended option MUST score highest on this lens (in order):

| Priority | Lens | Example |
|----------|------|---------|
| 1st | Operational simplicity | Fewer moving parts > elegant abstraction |
| 2nd | Dependency hygiene | In-house > new external library |
| 3rd | Archival over deletion | `tools/archive/` > `git rm` |
| 4th | Documentation discipline | ADR + rule > undocumented change |
| 5th | Zero-regression validation | Full test pass > speed |

These five lenses are the calibration vector for `author-gate-enforcement.md` §confidence scoring.

## Calibration Metrics (Red / Yellow / Green)

| Metric | Red | Yellow | Green |
|--------|-----|--------|-------|
| Author-Gate prompts per T2 session | >5 | 2-5 | ≤2 |
| Author-Gate prompts per T3 session | >8 | 3-8 | ≤4 |
| False stops (no real choice) | >2/session | 1-2/session | 0/session |
| Missed gates (silent architectural choice) | Any | — | 0 |
| Options per prompt | <2 or >4 | — | 2-4 |
| ⭐ Recommendation semantics | Star without dominance (top<0.85 or gap<0.12) | Star rule drifts across turns | Star iff `routing.rule_applied == "dominance_fires"` |
| `[confidence=0.NN]` prefix on every surfaced option | Missing on any option | Present on some | Present on 100% |

Red metrics are surface-level outage indicators; Yellow is acceptable but trending; Green is target.

## Continuous Execution Mandate (cadence)

Between Author-Gate decision points, Cursor Agent MUST execute all deterministic steps without interruption:

```
[Author-Gate] Select approach
→ [AUTO] Read files / query ADG
→ [AUTO] Edit
→ [AUTO] Run scoped tests
→ [AUTO] Commit + push
→ [Author-Gate] Next decision point (if any)
```

Stopping between [AUTO] steps = constitutional §6 violation.

## See for Full Doctrine

| Concern | File |
|---|---|
| Trigger doctrine (AG-1.1 to AG-1.11) | `author-gate-decision-points.md` |
| Pipeline + scoring + format + markers | `author-gate-enforcement.md` |
| Anti-pattern subcase | `anti-pattern-author-gate.md` |
| Categorical policy (A/B/C) | `approval-exception-policy.md` |

## Constitutional Cross-Reference

§6 (Author-Gate for ambiguous decisions). §30 (Author-Gate capture health).
