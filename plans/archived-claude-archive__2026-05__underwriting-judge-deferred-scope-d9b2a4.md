---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\underwriting-judge-deferred-scope-d9b2a4.md'
original_relative_path: '_archive\\2026-05\\underwriting-judge-deferred-scope-d9b2a4.md'
source_sha256: c982ba3a31664a8167af9a69333ba4d7fa8ed991f45a35489e6c1490abdb903e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: underwriting-judge-deferred-scope-d9b2a4

> **Status:** Not Started  
> **Parent plan:** apps-underwriting-ai-d3-rationale-judge-f2c8d5 (Completed)  
> **Notion:** TBD on registration  
> **DO NOT IMPLEMENT** — scope capture only

---

## Purpose

Captures all deferred scope items from the DS-R1–R8 implementation
(`apps-underwriting-ai-d3-rationale-judge-f2c8d5`). None of these items
are implemented. This plan exists to ensure nothing is lost.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.2 | Real LLM judge (Anthropic/Gemini API calls) | ~20k | ANTHROPIC_API_KEY + GOOGLE_API_KEY in env; holdout Spearman already ≥ 0.80 | Not Started | AnthropicJudge / GoogleJudge return float scores; calibration harness runs end-to-end against real API |
| W2 | P2.1–P2.2 | DS-R4 + DS-R7 (not yet implemented) | ~12k | W1 complete | Not Started | DS-R4 and DS-R7 acceptance tests pass |
| W3 | P3.1–P3.2 | Per-dim Spearman hardening (≥ 0.80 for all 5 dims) | ~10k | Additional human labels available | Not Started | Per-dim rho ≥ 0.80 for feature_derivation_correctness (0.74) and policy_compliance (0.75) |
| W4 | P4.1 | Judge CI in GitHub Actions (live API calls) | ~8k | Secrets configured in repo | Not Started | judge-calibration.yml workflow green with real API keys |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | AnthropicJudge real invocation in CI | `agentic_core/L3_orchestration/exit_eval/judges/anthropic_judge.py`, `.github/workflows/judge-calibration.yml` | Requires ANTHROPIC_API_KEY secret; currently only instantiates, never called in CI | ~8k | Not Started |
| P1.2 | GoogleJudge real invocation in CI | `agentic_core/L3_orchestration/exit_eval/judges/google_judge.py`, `.github/workflows/judge-calibration.yml` | Requires GOOGLE_API_KEY secret; GEMINI_API_KEY deprecated alias wired but untested | ~6k | Not Started |
| P1.3 | Judge retry-on-low for rationale_quality dim | `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` | retry-on-low policy exists but `judge_retry_on_low=True` never set for underwriting rubric | ~4k | Not Started |
| P2.1 | DS-R4 implementation | TBD — DS-R4 requirements not yet scoped | DS-R4 was not part of the completed plan; requirements unknown | ~6k | Not Started |
| P2.2 | DS-R7 implementation | TBD — DS-R7 requirements not yet scoped | DS-R7 was not part of the completed plan; requirements unknown | ~6k | Not Started |
| P3.1 | Per-dim Spearman: feature_derivation_correctness ≥ 0.80 | `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`, `tools/underwriting/_recalibrate_human_scores.py` | Current rho=0.74 with 20 examples; need more examples or better heuristic coverage for this dim | ~5k | Not Started |
| P3.2 | Per-dim Spearman: policy_compliance ≥ 0.80 | `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml` | Current rho=0.75; policy signal heuristic may need refinement | ~5k | Not Started |
| P4.1 | GitHub Actions judge-calibration.yml hardening | `.github/workflows/judge-calibration.yml` | Lint errors: invalid `needs: judge-calibration` reference (line 103); OPENAI_API_KEY / GOOGLE_API_KEY context access warnings | ~4k | Not Started |

---

## Deferred Scope Register

### DS-DEFER-1: Real LLM API calls in calibration CI

**From:** DS-R2 (Anthropic adapter), DS-R2 (Google adapter)  
**What was done:** Both judge adapters were implemented and instantiated correctly.
ANTHROPIC_API_KEY and GOOGLE_API_KEY are resolved from environment. The adapters
are wired into `run_judge_calibration.py`.

**What is NOT done:** The GitHub Actions `judge-calibration.yml` workflow does not
have the real API keys configured as secrets. CI currently runs in dry-run / fake-judge
mode only. Real end-to-end judge scoring against the holdout has not been validated
outside local developer runs.

**Action required:** Configure `ANTHROPIC_API_KEY` and `GOOGLE_API_KEY` in GitHub
repo secrets. Fix lint errors in `judge-calibration.yml` (invalid `needs` reference at
line 103; context access warnings for OPENAI_API_KEY / GOOGLE_API_KEY at lines 118–119).
Run workflow end-to-end with real judge invocations.

---

### DS-DEFER-2: DS-R4 and DS-R7 (unscoped)

**From:** Session context — DS-R4 and DS-R7 were listed in the requirements set but
were not assigned acceptance criteria in the completed plan.

**What is NOT done:** DS-R4 and DS-R7 have no implementation, no test, no acceptance
criteria captured. Their scope is unknown.

**Action required:** Scope DS-R4 and DS-R7 requirements explicitly before scheduling
implementation.

---

### DS-DEFER-3: Per-dim Spearman ≥ 0.80 for all 5 dims

**From:** DS-R5 gate design — the gate enforces ≥ 0.80 globally and ≥ 0.70 per-dim.
Two dims are below the 0.80 per-dim ceiling:

| Dim | Current rho | Gap to 0.80 |
|---|---|---|
| `feature_derivation_correctness` | 0.741 | −0.059 |
| `policy_compliance` | 0.750 | −0.050 |

**Root cause:** These dims have only 20 holdout examples each. The deterministic
heuristic scorer has limited signal for feature derivation (lacks structured formula
parsing) and policy compliance (limited policy-section citation patterns).

**Options (not yet chosen):**
1. Add 20 more labeled examples per dim to reduce sampling variance.
2. Extend the heuristic scorer with dim-specific feature signals.
3. Raise the per-dim threshold to 0.75 in the CI gate (matches current performance).
4. Accept the current values — per-dim 0.70 threshold already passes.

---

### DS-DEFER-4: Judge retry-on-low for rationale_quality dim

**From:** `apps-eval-harness-deferred-e4a1b7` W4 retry-on-low policy.

**What was done:** `AppSpecificEvaluator._score_against_rubric` already supports
retry-on-low when `run_context["judge_retry_on_low"]=True` and
`grader_type=llm_as_judge`.

**What is NOT done:** The `apps_underwriting_ai` rubric does not set
`judge_retry_on_low=True` for the `rationale_quality` dimension. The retry path is
dead code for this app.

**Action required:** Add `judge_retry_on_low: true` to the `rationale_quality`
dimension in `apps_underwriting_ai/config/domain_contract/threshold_profiles.yaml`
(or equivalent rubric config) and add a test covering the retry path.

---

### DS-DEFER-5: GitHub Actions judge-calibration.yml lint errors

**From:** IDE lint warnings surfaced during this session.

**Errors:**
- Line 103: `needs: judge-calibration` — invalid value; job cannot depend on itself
- Line 118: `OPENAI_API_KEY` — context access might be invalid (secret not defined)
- Line 119: `GOOGLE_API_KEY` — context access might be invalid (secret not defined)
- `runtime-certification.yml` line 390: `LOCAL_QWEN_ENDPOINT` — context access warning

**Action required:** Fix the `needs` self-reference. Add the missing secrets to GitHub
repo settings or gate the steps with `if: secrets.OPENAI_API_KEY != ''` conditions.

---

### DS-DEFER-6: Production-log mining for holdout expansion

**From:** `apps-eval-harness-deferred-e4a1b7` W5.P2 (parent W5.P2 deferred).

**What is NOT done:** The holdout dataset was authored from synthetic decision patterns.
Real production decision logs (with PII redaction) have not been mined to expand or
validate the holdout. The gap means the holdout may not reflect the distribution of
real underwriting decisions.

**Action required:** Design PII-redaction pipeline for production decision rationale
export. Seed holdout with ≥ 10 real examples per dim after redaction review.

---

### DS-DEFER-7: SSOT consolidation of legacy policy/threshold YAMLs

**From:** `apps-eval-harness-deferred-e4a1b7` W5.P4.

**What is NOT done:** Multiple YAML files define overlapping policy thresholds for
`apps_underwriting_ai` (e.g. `holdout_schema.yaml`, `threshold_profiles.yaml`,
sub-contract YAMLs). No SSOT consolidation pass has been done.

**Action required:** Audit and consolidate redundant threshold/policy YAML definitions
under a single canonical source per dimension.

---

## Gap Register

| ID | Description | Blocker? | Priority |
|---|---|---|---|
| DS-DEFER-1 | Real LLM API calls in CI (Anthropic + Gemini) | No | P3 |
| DS-DEFER-2 | DS-R4 and DS-R7 requirements unscoped | Yes (blocks completion) | P2 |
| DS-DEFER-3 | Per-dim Spearman ≥ 0.80 for 2 dims | No (0.70 threshold passes) | P3 |
| DS-DEFER-4 | retry-on-low wiring for rationale_quality | No | P4 |
| DS-DEFER-5 | judge-calibration.yml lint errors | No (advisory) | P3 |
| DS-DEFER-6 | Production-log mining for holdout expansion | No | P4 |
| DS-DEFER-7 | SSOT consolidation of policy/threshold YAMLs | No | P4 |
