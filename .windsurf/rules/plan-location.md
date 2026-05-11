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
5. Include a **`## Definition of Done`** section with at least 5 DoD rows (DoD-1..DoD-N) and a Verification-vs-Deferral table. Every plan touching an executable surface MUST have a smoke-run DoD row of the form `python -m <module> [args]` exits 0 + produces a recognizable artifact. RCA-only / doc-only / observational plans MAY set `dod_exempt: true` in frontmatter to skip this requirement — prose hand-waving is not an exemption. Enforced by CI gate `ops_scripts/ci/check_plan_definition_of_done.py` (PLAN-DOD).

A plan missing the wave summary table **or** the phase-level summary table **or** the `## Definition of Done` section (without `dod_exempt: true`) is **invalid and must not be marked Completed in Notion**.

> ⛔ **Failure precedent**: `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1` was marked W9 COMPLETE while `python -m apps_rg` raised ImportError on first import. A DoD smoke-run row would have made the regression auto-falsifiable. The DoD requirement (added 2026-05-09 by plan `apps-rg-runtime-wiring-completion-d4e8a1` W6) closes that failure mode.

> **History**: The `tools/utils/planning/token_estimator.py` (`ContextWindowEstimator`) module was retired 2026-04-24 and archived to `archives/tools_planning_20260424_obsolete/`. It served the 200k-window era; the 1M-window era makes pre-flight budget enforcement unnecessary friction. Plans still size phases for scope clarity, not for budget compliance.

## Notion Status Discipline (added 2026-05-11)

All new plans registered in Notion Plans DB **MUST** be created with Status="Not Started".

**The Invariant**: A plan's initial status is NEVER "In Progress", "Waiting", or any other state. Only "Not Started" (standard) or "Completed" (retrospective plans only) are valid at creation time.

**Why**: The "In Progress" at creation bug (RCA: `docs/rca/RCA_PLAN_STATUS_IN_PROGRESS_WRONG-b5d3e1.md`) caused plan tracking confusion and broke automation that depends on status state machine transitions.

**Canonical Creation Path** (use for all new plans):
```python
from tools.notion.plan_creation_helper import create_plan_in_notion

result = create_plan_in_notion(
    slug="my-plan-abc123",
    summary="Plan summary",
    ai_summary="- Target: ...",
    # Status defaults to "Not Started" — never override to "In Progress"
)
```

**Retrospective Plans Only** (documenting already-completed work):
```python
result = create_plan_in_notion(
    slug="retrospective-xyz789",
    summary="Retrospective documentation",
    ai_summary="- Target: ...",
    force_status="Completed",  # Only valid exception
)
```

**Defense Layers** (plan `holistic-plan-status-discipline-d4e8a1`):
| Layer | Component | Enforcement |
|-------|-----------|-------------|
| 1 | `plan_creation_helper.py` | Code-level enforcement, rejects wrong status |
| 2 | `pre_notion_plan_creation_gate.py` | Pre-flight hook validation |
| 3 | `post_cascade_plan_creation_audit.py` | Post-creation auto-correction |
| 4 | NP14 CI gate | Weekly drift detection in CI |
| 5 | Documentation | This section + template |

**Bypass** (emergency only): Set `NOTION_PLAN_STATUS_INITIAL_BYPASS=1` — logs warning but allows.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no Author-Gate prompt, no confirmation request.
