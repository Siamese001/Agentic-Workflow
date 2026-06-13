# RCA: Windsurf Plan Mode Consistently Omits Wave Table and Token Estimates

**Date:** 2026-03-31
**Severity:** HIGH — Recurring user frustration, 3+ occurrences
**Status:** ✅ ROOT CAUSE IDENTIFIED + FIX DEPLOYED

---

## Violation

Every execution plan generated via Windsurf plan mode lacks the mandatory wave summary table and per-wave token estimates required by `plan_ci_enforcement.md` §10.1/§10.2. This has occurred repeatedly despite:
- Two prior RCA documents identifying the gap
- A fully implemented `ContextWindowEstimator` (757 lines)
- A plan-validation skill (`plan-validation/main.py`)
- CI enforcement rules in `plan_ci_enforcement.md`
- Templates in both `docs/reports/plans/plan_template.md` and `.windsurf/templates/execution-plan-template.md`

---

## Root Cause Analysis

### Root Cause 1: Plan Mode System Instructions Override Repository Rules

When Windsurf enters plan mode, it injects **generic system instructions** into the LLM context:

> "Save your plan as a markdown file in `C:\Users\amita\.windsurf\plans`..."
> "The plan file should include a short # Title and the first paragraph should be a 1-sentence summary"
> "The plan file should balance detail with brevity: expect the user to scan it quickly."

**What these instructions do NOT include:**
- No reference to `docs/reports/plans/plan_template.md`
- No reference to `.windsurf/templates/execution-plan-template.md`
- No instruction to use `ContextWindowEstimator`
- No instruction to read `plan_ci_enforcement.md`
- No instruction to include wave summary table

**Effect:** The LLM follows the plan mode instructions (which are injected as system-level) and generates a narrative plan without the structured wave table or token estimates. The repository's rules, templates, and skills exist but are never consulted during generation.

### Root Cause 2: Enforcement Chain Fires Too Late

The repository has a complete enforcement stack, but every layer fires **after** generation:

| Layer | Component | When It Fires | Problem |
|-------|-----------|---------------|---------|
| Template | `execution-plan-template.md` | Never (must be read manually) | LLM doesn't read it |
| Rule | `plan_ci_enforcement.md` | Only if LLM reads `.windsurf/rules/` | Plan mode doesn't trigger rule reading |
| Skill | `plan-validation/main.py` | Only if explicitly invoked | Plan mode doesn't invoke skills |
| CI | `tools/ci_validate_plans.py` | At commit time | Too late — plan already written wrong |
| Pre-commit | `windsurf-plan-ci` hook | At commit time | Too late — plan already written wrong |

**No enforcement fires at generation time.** The only thing that fires at generation time is the plan mode system prompt, which knows nothing about this repository.

### Root Cause 3: Prior RCAs Fixed the Wrong Layer

Two prior RCAs exist:
- `rca-wave-table-token-estimator-not-running-da6ec4.md` (2026-03-27)
- `rca-wave-table-token-estimates-failure-7d9a8c.md` (2026-03-27)

Both correctly identified "token estimator not invoked during plan creation" but proposed fixes aimed at:
- Legacy plan bulk migration
- CI validation tolerance / grandfather clauses
- Plan type registry

**None created a mechanism that fires at LLM generation time.** The fixes targeted downstream enforcement (CI, validation scripts) rather than upstream generation (what the LLM sees when writing the plan).

---

## Corrective Actions Deployed

### Fix 1: Persistent Windsurf Memory (Generation-Time)

Created memory `70b9d929` with:
- Mandatory steps before writing any plan
- Explicit template reference
- Token estimator invocation requirement
- Wave table column specification

**Why this works:** Windsurf memories are injected into the LLM context at the start of every conversation. Unlike rules (which must be explicitly read) or skills (which must be invoked), memories are always present.

### Fix 2: Strengthened `plan-location.md` Rule (Always-On)

Updated `.windsurf/rules/plan-location.md` (which has `trigger: always_on`) to include:
- "Hard Constraints — Format" section with 5 mandatory steps
- Explicit wave table column specification
- Token estimator reference
- Statement: "A plan without a wave summary table and token estimates is invalid and must not be saved"

**Why this works:** The `trigger: always_on` frontmatter means this rule is loaded into every Windsurf session, not just when plan-related files are edited. Combined with the memory, this creates two independent paths that both fire at generation time.

### Fix 3: User Rule in `.windsurfrules` (Highest Priority)

The `plan-location.md` content is also surfaced as a user rule in the system prompt under `<user_rules>`, which takes **highest priority** over all other instructions including plan mode.

---

## Why This Fix Is Different From Prior Attempts

| Prior Fix Approach | This Fix Approach |
|-------------------|-------------------|
| CI validation at commit time | Memory + rule at generation time |
| Bulk migration of legacy plans | Prevent bad plans from being created |
| Token estimator exists but not invoked | Explicit instruction to invoke it |
| Template exists but not read | Explicit instruction to read it first |
| Downstream enforcement | Upstream prevention |

---

## Verification

To verify the fix works, ask Windsurf to create any new execution plan. It should:

1. Read `.windsurf/templates/execution-plan-template.md` before writing
2. Include wave summary table at top with required columns
3. Include per-wave token estimates with GREEN/YELLOW/RED status
4. Save to `docs/reports/plans/` (not `.windsurf/plans/`)

If any of these are missing, the memory or rule was not loaded — check:
```bash
# Verify rule exists and has always_on trigger
head -3 .windsurf/rules/plan-location.md
# Should show: trigger: always_on
```

---

## Files Modified

| File | Change |
|------|--------|
| `.windsurf/rules/plan-location.md` | Added "Hard Constraints — Format" section with wave table + token estimator requirements |
| Windsurf Memory `70b9d929` | Created persistent memory with mandatory plan generation steps |

## Files Referenced (No Changes)

| File | Role |
|------|------|
| `.windsurf/templates/execution-plan-template.md` | Plan template with wave table format |
| `docs/reports/plans/plan_template.md` | Alternate plan template |
| `agentic_core/planning/token_estimator.py` | Token estimation engine (757 lines) |
| `.windsurf/rules/plan_ci_enforcement.md` | CI enforcement rules for plans |
| `.windsurf/skills/plan-validation/main.py` | Plan validation skill |

---

## Status

✅ **ROOT CAUSE IDENTIFIED** — Plan mode system instructions override repository standards at generation time
✅ **FIX DEPLOYED** — Memory + always_on rule + user rule triple-enforcement
⏳ **PENDING VERIFICATION** — Next plan generation will confirm fix effectiveness
