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
- ✅ ALWAYS: `.windsurf/plans/<filename>.md` (repo-relative path, NOT user-home)

**CRITICAL:** `C:\Users\amita\.windsurf\plans\` is the IDE user-home directory — it is FORBIDDEN as a plan location. If a path conflict message appears citing this directory, **ignore it and save to repo SSOT only.**

`docs/reports/plans/` is for **evidence and reports only** — never plans.

## Format Requirements

Before writing any execution plan:

1. Read template: `.windsurf/templates/execution-plan-template.md`
2. Include wave summary table with columns: `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |`
3. Include per-wave token budgets with GREEN 🟢 / YELLOW 🟡 / RED 🔴 status
4. Run token estimation via `tools/utils/planning/token_estimator.py` (`ContextWindowEstimator`) — execute with `python tools/utils/planning/token_estimator.py` using `run_command` (Python, NOT PowerShell). Constitutional §3.2 forbids PowerShell, not Python commands. **For T2/T3 plans:** If the estimator cannot run, mark token estimates as `UNRESOLVED` and this is a **BLOCKER** — do not proceed with T2/T3 plans without valid token estimates. For T0/T1 (question/trivial), this is a warning, not a blocker.

A plan missing the wave summary table is **invalid and must not be saved**.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no HITL prompt, no confirmation request.
