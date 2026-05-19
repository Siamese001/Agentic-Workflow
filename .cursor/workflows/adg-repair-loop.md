---
description: Thin alias — ADG-scoped repair loop (/adg-repair-loop)
---

# /adg-repair-loop

**Tier:** Workflow alias only.

## Authority map

| Layer | SSOT |
|-------|------|
| Invariants | [adg-canonical-invariants.mdc](../rules/adg-canonical-invariants.mdc) |
| Repair protocol (full steps) | [adg-analysis-procedures.mdc](../rules/adg-analysis-procedures.mdc) §5 |
| P-band discipline | [adg-p-band-burn-down-discipline.mdc](../rules/adg-p-band-burn-down-discipline.mdc) |
| Tool routing | [graph-analysis/SKILL.md](../skills/graph-analysis/SKILL.md), [adg-sqlite/SKILL.md](../skills/adg-sqlite/SKILL.md) |
| P7 accelerator | [adg-p7-analyst-artifacts.mdc](../rules/adg-p7-analyst-artifacts.mdc) |

## Invocation steps

1. `adg_health` → confirm ADG MCP; refresh cache if stale (`/adg-redis-refresh` when needed).
2. Select cluster / scoped tests via ADG (never manual path expansion) — see §5 in `adg-analysis-procedures.mdc`.
3. Patch smallest seam; prove with scoped pytest; emit `ADG_REPAIR_LITMUS` when required.
4. Author-Gate if repair class is ambiguous.

⛔ No full-suite runs until convergence. No duplicate repair steps in this file.
