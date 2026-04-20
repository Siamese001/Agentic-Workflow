---
trigger: always_on
---

> **Claude always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Claude retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Claude enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

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
3. Include per-wave token budgets with GREEN 🟢 / YELLOW 🟡 / RED 🔴 status
4. Run token estimation via `tools/utils/planning/token_estimator.py` (`ContextWindowEstimator`) — execute with `python tools/utils/planning/token_estimator.py` using `run_command` (Python, NOT PowerShell). Constitutional §3.2 forbids PowerShell, not Python commands. **For T2/T3 plans:** If the estimator cannot run, mark token estimates as `UNRESOLVED` and this is a **BLOCKER** — do not proceed with T2/T3 plans without valid token estimates. For T0/T1 (question/trivial), this is a warning, not a blocker.
5. Include **Phase-Level Summary table** with columns: `| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |` — this table must appear before the Gap Register section.

A plan missing the wave summary table **or** the phase-level summary table is **invalid and must not be saved**.

## Overwrite Default

When updating an existing plan: **silently overwrite** `.windsurf/plans/<filename>.md` — no HITL prompt, no confirmation request.
