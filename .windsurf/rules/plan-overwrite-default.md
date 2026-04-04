---
trigger: always_on
---

# Plan Overwrite Default — Canonical Version Authority

**Rule:** When updating execution plans, AUTOMATICALLY overwrite the canonical version at `docs/reports/plans/<filename>.md` WITHOUT asking for confirmation.

**Why:** The user explicitly requested this behavior to avoid being prompted on every plan update.

## Canonical Version Authority

- **SSOT Location:** `docs/reports/plans/`
- **Prohibited Location:** `.windsurf/plans/` — never save here
- **Default Action:** Overwrite in place, no confirmation prompt

## Execution Discipline

When a plan update is requested:

1. **NO HITL PROMPT** — do not ask "should I overwrite..."
2. **Write directly** to `docs/reports/plans/<filename>.md`
3. **Maintain wave table** — preserve wave summary format per `.windsurf/rules/plan_ci_enforcement.md`
4. **Preserve hex suffix** — keep the existing filename (e.g., `-d0cb16`)

## Applicability

This rule applies to:
- Plan alignment updates
- Wave progress updates  
- Token estimate refreshes
- Success criteria revisions
- Any rewrite of an existing `docs/reports/plans/*.md` file

## Violation

Asking the user "should I overwrite..." when updating a plan at `docs/reports/plans/` is a RULE VIOLATION.

## Reference

- Plan location rule: `.windsurf/rules/plan-location.md`
- Plan CI enforcement: `.windsurf/rules/plan_ci_enforcement.md`
- Template: `.windsurf/templates/execution-plan-template.md`
