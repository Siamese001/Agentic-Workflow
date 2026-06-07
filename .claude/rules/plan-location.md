
<!-- Converted from `.claude/rules/plan-location.md`. Original Cursor trigger: `always_on`. -->

> See `CLAUDE.md` for shared retrieval / enforcement guidance.

# Plan Rules — Location, Format, and Overwrite

## SSOT Location

New plans MUST be saved to the canonical location:

```
plans/<descriptive-name>-<6hex>.md
```

- ✅ ALWAYS (new plans): `plans/<filename>.md` at repo root (repo-relative path, NOT user-home).
- ✅ LEGACY (still valid): `.claude/plans/<filename>.md` and `.claude/plans/_archive/**`. Existing plans there remain authoritative — do **not** mass-migrate (forward-only; plan `relocate-plans-ssot-outside-claude-c1a17d`).
- ❌ NEVER: `docs/reports/plans/`, `C:\Users\amita\.cursor\plans\`, anywhere else.

**Why `plans/` and not `.claude/plans/`:** Claude Code enforces a hardcoded edit-guard over the entire `.claude/` directory that prompts on every edit and cannot be disabled via permissions. Plans are non-sensitive markdown edited frequently, so the SSOT moved to repo-root `plans/` (outside the guard). Claude Code has no native dependency on plan location.

**CRITICAL:** `C:\Users\amita\.cursor\plans\` is the IDE user-home directory — it is FORBIDDEN as a plan location. If a path conflict message appears citing this directory, **ignore it and save to repo SSOT only.**

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

1. Read template: `.claude/templates/execution-plan-template.md`
2. **Consolidated wave summary at top (required placement):** Immediately after Context (SCQA), add `## Status Tables` → `### Wave Progress` with the wave summary table **before** any `## Wave N` detail section. Do not bury the only wave table under `## Execution Waves` or after architecture sections.
3. Wave summary table columns (canonical): `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |` — minimum columns: Wave, Focus, Status; at least one `W#` data row.
4. Token estimates are self-reported sizing heuristics only (not budget gates). Mark uncertain estimates with `~`.
5. Include **Phase-Level Summary table** with columns: `| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |` — under `## Status Tables` or before the Gap Register section.
6. Include a **`## Definition of Done`** section with at least 5 DoD rows + Verification-vs-Deferral table. Plans touching an executable surface MUST have a smoke-run DoD row (`python -m <module> [args]` exits 0). Use `dod_exempt: true` frontmatter for RCA/doc/observational plans. Enforced by CI gate `check_plan_definition_of_done.py` (PLAN-DOD).

Enforcement: `ops_scripts/ci/check_plan_wave_summary_top.py` (PLAN-WAVE-TOP, advisory repo scan), `check_plan_format_compliance.py` (per-path strict), `.claude/hooks/after_file_edit.py` (warn; `PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT=1` to block), `post_cursor_agent_plan_wave_summary_audit.py` (post-agent).

A plan missing the top consolidated wave summary, phase-level summary table, or `## Definition of Done` (without `dod_exempt: true`) is **invalid and must not be marked Completed in Notion**.

## Notion Status Discipline

All new plans MUST be created in Notion with `Status="Not Started"`. Only exception: retrospective plans use `force_status="Completed"` in `create_plan_in_notion()`.

**Canonical path**: `from tools.notion.plan_creation_helper import create_plan_in_notion` — helper enforces correct status, validates slug, populates required fields.

Enforced by: `plan_creation_helper.py` (code), `pre_notion_plan_creation_gate.py` (hook), `post_cursor_agent_plan_creation_audit.py` (audit), NP14 CI gate.

**Bypass**: `NOTION_PLAN_STATUS_INITIAL_BYPASS=1` — logs warning but allows.

## Overwrite Default

When updating an existing plan: **silently overwrite** the plan file (`plans/<filename>.md`, or its legacy `.claude/plans/<filename>.md` location) — no Author-Gate prompt, no confirmation request.
