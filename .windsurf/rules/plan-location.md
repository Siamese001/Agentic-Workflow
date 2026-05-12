---
trigger: always_on
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

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

## When a Plan Is Required

A plan is required when ANY of the following apply:
- Task is T2 or T3 (see constitutional.md Tier Classification)
- Work crosses architectural layers
- Output has irreversible side effects (deletion, migration, schema change)
- Scope is ambiguous or has multiple valid approaches

A plan is NOT required for T0/T1 work, single-file single-concern changes, typo fixes, or pure questions.

## Format Requirements

Before writing any execution plan:

1. Read template: `.windsurf/templates/execution-plan-template.md`
2. Include wave summary table with columns: `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |`
3. Token estimates are self-reported sizing heuristics only (not budget gates). Mark uncertain estimates with `~`.
4. Include **Phase-Level Summary table** with columns: `| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |` — this table must appear before the Gap Register section.
5. Include a **`## Definition of Done`** section with at least 5 DoD rows + Verification-vs-Deferral table. Plans touching an executable surface MUST have a smoke-run DoD row (`python -m <module> [args]` exits 0). Use `dod_exempt: true` frontmatter for RCA/doc/observational plans. Enforced by CI gate `check_plan_definition_of_done.py` (PLAN-DOD).

A plan missing the wave summary table, phase-level summary table, or `## Definition of Done` (without `dod_exempt: true`) is **invalid and must not be marked Completed in Notion**.

## Notion Status Discipline

All new plans MUST be created in Notion with `Status="Not Started"`. Only exception: retrospective plans use `force_status="Completed"` in `create_plan_in_notion()`.

**Canonical path**: `from tools.notion.plan_creation_helper import create_plan_in_notion` — helper enforces correct status, validates slug, populates required fields.

Enforced by: `plan_creation_helper.py` (code), `pre_notion_plan_creation_gate.py` (hook), `post_cascade_plan_creation_audit.py` (audit), NP14 CI gate.

**Bypass**: `NOTION_PLAN_STATUS_INITIAL_BYPASS=1` — logs warning but allows.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no Author-Gate prompt, no confirmation request.
