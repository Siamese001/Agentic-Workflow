---
trigger: always_on
---
# Plan Rules — Location, Format, and Overwrite

## SSOT Location

Plans MUST be saved to exactly ONE location:

```
.windsurf/plans/<descriptive-name>-<6hex>.md
```

- ❌ NEVER: `docs/reports/plans/`, `C:\Users\amita\.windsurf\plans\`, anywhere else
- ✅ ALWAYS: `.windsurf/plans/<filename>.md`

`docs/reports/plans/` is for **evidence and reports only** — never plans.

## Format Requirements

Before writing any execution plan:

1. Read template: `.windsurf/templates/execution-plan-template.md`
2. Include wave summary table with columns: `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |`
3. Include per-wave token budgets with GREEN 🟢 / YELLOW 🟡 / RED 🔴 status
4. Run token estimation via `agentic_core/planning/token_estimator.py` (`ContextWindowEstimator`)

A plan missing the wave summary table is **invalid and must not be saved**.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no HITL prompt, no confirmation request.
