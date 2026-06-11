---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\rag-dim-activation-c4f8b2.md'
original_relative_path: 'rag-dim-activation-c4f8b2.md'
source_sha256: b634464d39b132cad6fe176b700b31809cc538345ec104f65875c22792563813
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RAG Dim Activation

**Plan ID**: `rag-dim-activation-c4f8b2`
**Status**: Draft
**Parent plan**: `apps-core-contract-rectification-a8f3c2` (Completed — W5.1 deferred here)
**Created**: 2026-05-03

---

## Preconditions (MUST complete before Wave 1 begins)

| Plan | What it delivers | Status |
|---|---|---|
| `holdout-corpus-authoring-b5d2f6` | Human-labeled holdout corpus for RAG dim scoring | Draft |
| `judge-spearman-calibration-a7e4c9` | RAG judge impls with Spearman ρ ≥ 0.80 vs holdout | Draft |

**This plan MUST NOT execute Wave 1 until both precondition plans reach `Completed`.**

Precondition gate check (run before W1):
```
python ops_scripts/ci/check_grounded_rag_active.py --app apps_qna
```
If any RAG dim is missing a scorer (`NO_UNIMPL_JUDGES` ERROR), stop — preconditions are not met.

---

## Context

Five grounded apps have 3 RAG dims each (`context_recall`, `context_precision`, `answer_relevancy`) declared in their rubrics with:
- `weight: 0.0`
- `fail_closed_if_unknown: false`
- Listed in `intentional_failopen_dims` on their threshold profiles

This configuration is intentionally fail-open, established by plan `apps-eval-harness-closeout-b7c9d2` W1.

The AEH3 gate (`ops_scripts/ci/check_grounded_rag_active.py`) enforces the activation contract:
- While dims are in `intentional_failopen_dims` → emits INFO (expected)
- Once removed from `intentional_failopen_dims` but `weight==0.0` or `fail_closed_if_unknown==false` → emits ERROR

The test skeleton (`tests/_apps_contract/test_rag_dims_active.py`, 28 tests) also guards the deferred state and will need its assertions flipped in W3.

**C0 FEC producers are already landed** (plan `apps-*-c0-fec-producer-wiring-*`, 2026-05-03). All 5 grounded apps ship `ExitReviewPacket.final_evidence_contract` and auto-upgrade `grounded=True` when `c0_retrieval_sources` populates. No cert changes needed.

---

## Wave Structure

| Wave | Focus | Scope | Status |
|---|---|---|---|
| W1 | Precondition verification | Confirm scorer impls + holdout corpus present | 🔲 TODO |
| W2 | YAML activation | Flip 5 apps × 3 dims: `weight>0`, `fail_closed=true`, remove from `intentional_failopen_dims` | 🔲 TODO |
| W3 | Test flip | Update `test_rag_dims_active.py` deferred-state → active-state assertions | 🔲 TODO |
| W4 | Regression verification | Full `tests/_apps_contract/` suite passes; AEH3 gate ERROR=0 | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Scorer presence check | `check_grounded_rag_active.py` + manual import check | Precondition not met = hard stop | ~1K | 🔲 TODO |
| 1.2 | Holdout + Spearman audit | Read calibration reports; confirm ρ ≥ 0.80 for all 3 dims | Report format may vary | ~1K | 🔲 TODO |
| 2.1 | Rubric weight flip — batch 1 (qna, research) | `apps_qna/config/domain_contract/eval_rubrics.yaml`, `apps_research/config/domain_contract/eval_rubrics.yaml` | Must not break existing non-RAG dims | ~2K | 🔲 TODO |
| 2.2 | Rubric weight flip — batch 2 (rfp, exec, underwriting_ai) | Same files for 3 remaining apps | Same | ~2K | 🔲 TODO |
| 2.3 | Threshold profile update — all 5 apps | Remove `context_recall`, `context_precision`, `answer_relevancy` from `intentional_failopen_dims` | Must remove all 3 per app atomically | ~2K | 🔲 TODO |
| 3.1 | Flip test deferred-state → active-state | `tests/_apps_contract/test_rag_dims_active.py` | 5 parametrized tests × 3 dims each | ~2K | 🔲 TODO |
| 4.1 | Full suite regression + gate verification | `pytest tests/_apps_contract/ -p no:xdist` + `check_grounded_rag_active.py` | Expect INFO=0 (all dims now active) | ~1K | 🔲 TODO |

---

## Files In Scope

### W2 — YAML changes (15 dim flips across 10 files)

**eval_rubrics.yaml** (5 files — set `weight: 0.15`, `fail_closed_if_unknown: true` on all 3 RAG dims):
- `apps_qna/config/domain_contract/eval_rubrics.yaml`
- `apps_research/config/domain_contract/eval_rubrics.yaml`
- `apps_rfp/config/domain_contract/eval_rubrics.yaml`
- `apps_exec/config/domain_contract/eval_rubrics.yaml`
- `apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml`

**threshold_profiles.yaml** (5 files — remove RAG dims from `intentional_failopen_dims`):
- `apps_qna/config/domain_contract/threshold_profiles.yaml`
- `apps_research/config/domain_contract/threshold_profiles.yaml`
- `apps_rfp/config/domain_contract/threshold_profiles.yaml`
- `apps_exec/config/domain_contract/threshold_profiles.yaml`
- `apps_underwriting_ai/config/domain_contract/threshold_profiles.yaml`

### W3 — Test changes (1 file)

- `tests/_apps_contract/test_rag_dims_active.py` — flip 4 deferred-state test groups to active-state assertions

### No changes needed

- `ops_scripts/ci/check_grounded_rag_active.py` — AEH3 gate already enforces; no edits
- `agentic_core/` — no spine changes
- `apps_*/cert/` — FEC producers already landed; no changes

---

## Exact YAML Changes (W2)

### eval_rubrics.yaml — per affected dim in each of 5 apps

```yaml
# BEFORE (deferred state)
- dimension_id: context_recall
  weight: 0.0
  grader_type: llm_as_judge
  fail_closed_if_unknown: false

# AFTER (active state)
- dimension_id: context_recall
  weight: 0.15
  grader_type: llm_as_judge
  fail_closed_if_unknown: true
```

Same flip for `context_precision` (weight: 0.15) and `answer_relevancy` (weight: 0.15).

> **Weight rationale**: 0.15 per dim × 3 dims = 0.45 total RAG contribution. Matches OpenAI canonical baselines
> (`context_recall: 0.85`, `context_precision: 0.70`, `answer_relevancy: 0.80`) established in `apps-eval-harness-closeout-b7c9d2` W1.
> Adjust post-activation based on production distribution if needed.

### threshold_profiles.yaml — remove from intentional_failopen_dims

```yaml
# BEFORE
intentional_failopen_dims:
  - context_recall
  - context_precision
  - answer_relevancy

# AFTER — remove the section entirely (or set to empty list)
# intentional_failopen_dims: []
```

---

## Test Assertion Flip (W3)

`tests/_apps_contract/test_rag_dims_active.py` currently has 4 deferred-state test groups:

| Test | Current assertion | Post-activation assertion |
|---|---|---|
| `test_rag_dims_in_intentional_failopen_while_deferred` | dim IN failopen → pass | dim NOT IN failopen → pass |
| `test_rag_dims_weight_zero_while_deferred` | weight == 0.0 → pass | weight > 0.0 → pass |
| `test_rag_dims_fail_open_while_deferred` | fail_closed == False → pass | fail_closed == True → pass |
| `test_gate_reports_only_info_for_deferred_apps` | no ERRORs → pass | no ERRORs → pass (unchanged — gate should still be clean) |

Rename deferred-state tests with `_deferred` suffix or delete and replace with active-state equivalents.

---

## Out of Scope

- RAG scorer implementation (belongs in `judge-spearman-calibration-a7e4c9`)
- Holdout corpus creation (belongs in `holdout-corpus-authoring-b5d2f6`)
- Any changes to `agentic_core` spine
- Per-app FEC producers (already completed)
- Weight tuning beyond initial 0.15 baseline (post-activation operational concern)
- Adding new RAG dims beyond the 3 established dims

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| RAG dim weight | > 0.0 on all 3 dims × 5 apps | `check_grounded_rag_active.py` ERROR=0 WARN=0 INFO=0 |
| fail_closed_if_unknown | `true` on all 3 dims × 5 apps | Same gate |
| intentional_failopen_dims | Empty / absent on all 5 apps | Same gate |
| Test suite | 827+ passed, 0 failures | `pytest tests/_apps_contract/ -p no:xdist -q` |
| AEH3 gate | ERROR=0 WARN=0 INFO=0 | `python ops_scripts/ci/check_grounded_rag_active.py` |
| No regression in non-RAG dims | Gate AEH1 still green | `python ops_scripts/ci/check_app_domain_harness_parity.py` |

---

## Rollback

If activation causes run failures (GRADER_UNKNOWN_SENTINEL → fail-close) before scorers are wired:
1. Re-add dims to `intentional_failopen_dims` on affected apps
2. Flip `weight: 0.0`, `fail_closed_if_unknown: false`
3. File bug against `judge-spearman-calibration-a7e4c9`

---

PLAN_CREATED: plan=rag-dim-activation-c4f8b2 waves=4 phases=7 tokens=~11K parent=apps-core-contract-rectification-a8f3c2 status=Draft preconditions=holdout-corpus-authoring-b5d2f6,judge-spearman-calibration-a7e4c9
