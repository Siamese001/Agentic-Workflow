---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\underwriting-judge-remaining-deferred-b3c1f9.md'
original_relative_path: '_archive\\2026-05\\underwriting-judge-remaining-deferred-b3c1f9.md'
source_sha256: dde9b231f4c93cea2e9c8fba62246c647caaa7cad069dbe2962aaab86283c7fc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: underwriting-judge-remaining-deferred-b3c1f9

> **Status:** Not Started  
> **Parent plan:** underwriting-judge-deferred-scope-d9b2a4 (Completed)  
> **Notion:** TBD on registration  
> **DO NOT IMPLEMENT** — scope capture only

---

## Purpose

Captures all deferred scope items that remain **unimplemented** after the
`underwriting-judge-deferred-scope-d9b2a4` plan completed. Items that were
completed in that plan (DS-R7 interactive prompt, P1.3 retry-on-low, W3
per-dim Spearman hardening, W4-P4.1 secret-env lint fixes) are explicitly
excluded from this register.

---

## What Was Completed (excluded from this plan)

| Item | Completed in |
|---|---|
| DS-R7: `--non-interactive` flag + `_prompt_jd_interactive` + `jd_payload` validation | `underwriting-judge-deferred-scope-d9b2a4` |
| P1.3: `judge_retry_on_low=True` wired in `apps_underwriting_ai/__main__.py` | `underwriting-judge-deferred-scope-d9b2a4` |
| W3: `_score_feature_derivation` + `_score_extended_policy_citation` + `_compute_score_for_dim` | `underwriting-judge-deferred-scope-d9b2a4` |
| W4-P4.1: `OPENAI_API_KEY` / `GOOGLE_API_KEY` secret `|| ''` fallbacks in `judge-calibration.yml` | `underwriting-judge-deferred-scope-d9b2a4` |
| DS-DEFER-5 partial: `needs: judge-calibration` self-reference removed | prior session |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.2 | Real LLM judge end-to-end in CI (Anthropic + Google) | ~20k | `ANTHROPIC_API_KEY` + `GOOGLE_API_KEY` already configured in CI secrets and local `.env` | Not Started | `judge-calibration.yml` runs real API calls; AnthropicJudge + GoogleJudge return float scores; Spearman logged |
| W2 | P2.1 | DS-R4 scoping + implementation | ~12k | DS-R4 requirements defined and agreed | Not Started | DS-R4 acceptance tests pass |
| W3 | P3.1–P3.2 | Per-dim Spearman ≥ 0.80 for all 5 dims | ~15k | Additional human-labeled examples available OR holdout expanded with synthetic diversity | Not Started | Per-dim rho ≥ 0.80 for `feature_derivation_correctness` (currently 0.740) and `policy_compliance` (currently 0.750) |
| W4 | P4.1–P4.2 | Production-log mining + holdout expansion | ~20k | PII-redaction pipeline available; compliance review complete | Not Started | ≥10 real examples per dim in holdout; holdout distribution matches production |
| W5 | P5.1 | YAML SSOT consolidation for `apps_underwriting_ai` policy/threshold configs | ~10k | No active feature work touching the YAMLs | Not Started | Single canonical source per dimension threshold; legacy duplication removed |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | AnthropicJudge real invocation in CI | `agentic_core/L3_orchestration/exit_eval/judges/anthropic_judge.py`, `.github/workflows/judge-calibration.yml` | `ANTHROPIC_API_KEY` already configured; adapter implemented but never called in CI real-run | ~8k | Not Started |
| P1.2 | GoogleJudge real invocation in CI | `agentic_core/L3_orchestration/exit_eval/judges/google_judge.py`, `.github/workflows/judge-calibration.yml` | `GOOGLE_API_KEY` already configured; `GEMINI_API_KEY` deprecated alias wired but untested at CI level | ~6k | Not Started |
| P2.1 | DS-R4 requirements scoping + implementation | TBD — DS-R4 has no acceptance criteria yet | DS-R4 was listed in requirements set but never scoped; must define before scheduling | ~12k | Not Started |
| P3.1 | Per-dim Spearman: `feature_derivation_correctness` ≥ 0.80 | `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`, `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | Current rho=0.740; gap=−0.060; 20-example subset has high sampling variance; heuristic signal covers formula/numeric terms but misses structured feature-key enumeration patterns | ~8k | Not Started |
| P3.2 | Per-dim Spearman: `policy_compliance` ≥ 0.80 | `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`, `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | Current rho=0.750; gap=−0.050; extended citation patterns (12 CFR, Reg B, ECOA, TILA, HMDA, ATR) added in W3 but holdout examples don't exercise full discriminating range | ~7k | Not Started |
| P4.1 | PII-redaction pipeline design | `tools/underwriting/` (new), compliance design doc | Requires compliance sign-off; no redaction pipeline exists; legal review needed before any production data touches the repo | ~10k | Not Started |
| P4.2 | Holdout expansion with real examples | `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml` | Depends on P4.1 PII-redaction approval; currently 20 synthetic examples per dim | ~8k | Not Started |
| P5.1 | YAML SSOT consolidation | `apps_underwriting_ai/holdout/holdout_schema.yaml`, `apps_underwriting_ai/config/domain_contract/threshold_profiles.yaml`, sub-contract YAMLs | Multiple YAML files overlap on policy thresholds; no audit done; no canonical source designated | ~10k | Not Started |

---

## Deferred Scope Register

### DS-REMAIN-1: Real LLM API calls in calibration CI

**From:** DS-DEFER-1 (`underwriting-judge-deferred-scope-d9b2a4`)  
**What is NOT done:** The `judge-calibration.yml` workflow runs only in
dry-run / fake-judge mode in CI. Real API calls to Anthropic and Google
Gemini have not been validated in the GitHub Actions environment.

**Status:** Keys already configured in CI secrets and local `.env`.

**Remaining action:**
1. Verify `judge-calibration.yml` `real-judge-run` job triggers correctly end-to-end
2. Confirm Spearman rho is logged per-dim in CI output

---

### DS-REMAIN-2: DS-R4 requirements unscoped

**From:** DS-DEFER-2 (`underwriting-judge-deferred-scope-d9b2a4`)  
**What is NOT done:** DS-R4 has no implementation, no test, and no
acceptance criteria. Its scope is completely unknown. DS-R7 was implemented
this session and is now closed.

**Action required:** Pull DS-R4 requirement definition from the original
requirements source and author acceptance criteria before scheduling any
implementation work.

---

### DS-REMAIN-3: Per-dim Spearman ≥ 0.80 ceiling

**From:** DS-DEFER-3 (`underwriting-judge-deferred-scope-d9b2a4`)  
**What was done in W3:** Added `_score_feature_derivation` (numeric ratio +
formula term signals, weight 0.45) and `_score_extended_policy_citation`
(12 CFR, Reg B, ECOA, TILA, HMDA, ATR patterns, weight 0.20). Both dims
now pass the CI threshold of ≥ 0.70.

**What remains:** The *ceiling* target of ≥ 0.80 per-dim is not yet met:

| Dim | Post-W3 rho | Gap to 0.80 |
|---|---|---|
| `feature_derivation_correctness` | 0.740 | −0.060 |
| `policy_compliance` | 0.750 | −0.050 |

**Options (not yet chosen):**
1. Add ≥10 more labeled examples per dim with better signal diversity
2. Further extend heuristic scorer with structured `risk_*` key enumeration
3. Accept current values — 0.70 CI threshold already passes

---

### DS-REMAIN-4: Production-log mining for holdout expansion

**From:** DS-DEFER-6 (`underwriting-judge-deferred-scope-d9b2a4`)  
**What is NOT done:** All 100 holdout examples are synthetic. No real
production underwriting decision rationales have been incorporated.

**Blockers:**
- Compliance sign-off required for PII redaction of production decisions
- Redaction pipeline does not exist

**Action required:** Design and get compliance approval for PII-redaction
pipeline before mining any production logs.

---

### DS-REMAIN-5: YAML SSOT consolidation

**From:** DS-DEFER-7 (`underwriting-judge-deferred-scope-d9b2a4`)  
**What is NOT done:** Multiple YAML files in `apps_underwriting_ai/` define
overlapping policy thresholds and holdout schema. No SSOT consolidation
audit has been performed.

**Files with potential overlap:**
- `apps_underwriting_ai/holdout/holdout_schema.yaml`
- `apps_underwriting_ai/config/domain_contract/threshold_profiles.yaml`
- `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml` (inline thresholds)

**Action required:** Audit all YAML threshold/policy definitions and
consolidate under a single canonical source per dimension.

---

## Gap Register

| ID | Description | Blocker? | Priority |
|---|---|---|---|
| DS-REMAIN-1 | Real LLM API calls in CI (Anthropic + Google secrets) | No (CI dry-run passes) | P3 |
| DS-REMAIN-2 | DS-R4 requirements unscoped | Yes (blocks implementation) | P2 |
| DS-REMAIN-3 | Per-dim Spearman ≥ 0.80 ceiling (2 dims at 0.74/0.75) | No (≥0.70 CI threshold passes) | P3 |
| DS-REMAIN-4 | Production-log mining (PII redaction + compliance) | Yes (compliance gate) | P4 |
| DS-REMAIN-5 | YAML SSOT consolidation | No | P4 |

---

## Non-Goals

- Implementing any item in this plan — this is a scope-capture register only
- Changing CI thresholds as a workaround for per-dim Spearman gaps
- Any production data access without compliance approval
