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
3. Token estimates are **self-reported by Cascade** based on scope (files touched, lines changed, complexity). They are sizing heuristics only, not budget gates — the 1M context window (Opus 4.7+) makes historical token-estimation tooling obsolete (see 2026-04-24 decision). Use your own judgment; mark uncertain estimates with `~`.
4. Include **Phase-Level Summary table** with columns: `| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |` — this table must appear before the Gap Register section.

A plan missing the wave summary table **or** the phase-level summary table is **invalid and must not be saved**.

> **History**: The `tools/utils/planning/token_estimator.py` (`ContextWindowEstimator`) module was retired 2026-04-24 and archived to `archives/tools_planning_20260424_obsolete/`. It served the 200k-window era; the 1M-window era makes pre-flight budget enforcement unnecessary friction. Plans still size phases for scope clarity, not for budget compliance.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no Author-Gate prompt, no confirmation request.
