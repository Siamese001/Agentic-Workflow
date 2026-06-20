---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-qna-judge-calibration-deferred-d4e8f2.md'
original_relative_path: '_archive\\2026-05\\apps-qna-judge-calibration-deferred-d4e8f2.md'
source_sha256: 1443282f24ddea99c858c821615dd3a305886d222f1d1c4ca3f53d3718780ade
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-judge-calibration-deferred-d4e8f2
plan_type: tracker
parent_plan: apps-qna-deferred-e5-f7a2b1
---

# apps_qna — Judge Calibration + C0 FEC Producer Deferred Items

Open deferred items from the completed `apps-qna-deferred-e5-f7a2b1` plan that were
explicitly out-of-scope at closeout: (1) human analyst calibration of the LLM judge
holdout corpus, and (2) C0 FEC producer binding for the 5 grounded apps.

**Parent Plan**: `.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md` (Completed 2026-05-06)
**Created**: 2026-05-06

---

## Context (SCQA)

- **Situation** — `apps-qna-deferred-e5-f7a2b1` is fully closed. All 5 waves done. The
  three RAG judges (`context_recall`, `context_precision`, `answer_relevancy`) have
  dual-path LLM+heuristic scoring with env auto-build. Tier 1 (heuristic sanity, 120ex)
  and Tier 2 (semantic alignment, 90ex) calibration corpora exist. The C0 FEC producer
  binding is also unresolved across 5 grounded apps (carried forward from
  `apps-eval-harness-closeout-b7c9d2` BLOCKER #4).

- **Complication** — The Tier 2 corpus was seeded with synthetic labels, not domain-expert
  human labels. The Spearman correlation baseline (context_recall/precision 1.0,
  answer_relevancy LLM-backed 0.7931) is only as reliable as those labels. Until a human
  analyst reviews and validates the semantic corpus, the calibration is "promotion eligible"
  in structure but not in ground truth. Separately, the 5 grounded apps have no FEC
  producer wiring, meaning the C0 retrieval evidence chain is incomplete for cert.

- **Question** — How do we close the human-labeling gap for judge calibration and the
  C0 FEC producer gap for the grounded apps?

- **Answer** — Two independent work streams: (D1) domain-expert review of the 90-example
  semantic corpus + updated Spearman baselines; (D2) FEC producer binding for the 5
  grounded apps following the pattern from `apps_qna/cert/fec_producer.py`.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_qna/holdout/rag_judge_holdout_semantic.yaml` | Corpus to be human-reviewed | 🔲 |
| `tests/_apps_contract/test_e2_llm_judge_calibration.py` | Calibration test to rerun after relabeling | 🔲 |
| `apps_qna/cert/fec_producer.py` | Pattern source for FEC producer binding | 🔲 |
| `apps_eval/cert/fec_producer.py`, `apps_research/cert/fec_producer.py` (etc.) | 5 grounded apps to wire | 🔲 |
| `ops_scripts/ci/check_app_domain_harness_parity.py` | Gate that fires BLOCKER #4 | 🔲 |

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status |
|------|-------|-------------|--------|
| D1 | Human analyst review + relabeling of 90-example semantic corpus | ~10K | ✅ DONE |
| D2 | C0 FEC producer binding for 5 grounded apps | ~25K | ✅ DONE |
| D3 | Rerun calibration tests + update Spearman baselines in plan + Notion | ~5K | ✅ DONE |

---

## Out Of Scope

- Expanding the holdout corpus beyond the existing 90-example semantic set (separate task).
- Changing judge prompt templates or scoring logic (E2 is closed).
- Any new judge types beyond the 3 RAG judges.
- Production log mining / PII-redacted label collection (parent plan W5.P2, separate plan slot).
- Holdout vs dev eval-set partition changes (parent plan W5.P1, separate plan slot).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| D1.1 | Domain-expert review of semantic corpus | `apps_qna/holdout/rag_judge_holdout_semantic.yaml` | Human-labeled scores may shift from synthetic baseline | ~5K | ✅ DONE |
| D1.2 | Update corpus YAML with validated human scores | `apps_qna/holdout/rag_judge_holdout_semantic.yaml` | Score drift may lower Spearman; adjust thresholds if needed | ~5K | ✅ DONE |
| D2.1 | FEC producer binding — apps_eval + apps_research | `apps_eval/cert/fec_producer.py`, `apps_research/cert/fec_producer.py` | Must follow apps_qna/cert/fec_producer.py pattern | ~8K | ✅ DONE |
| D2.2 | FEC producer binding — apps_rfp + apps_exec + apps_underwriting_ai | `apps_rfp/cert/fec_producer.py`, `apps_exec/cert/fec_producer.py`, `apps_underwriting_ai/cert/fec_producer.py` | Same pattern; gate suppression (`intentional_failopen_dims`) to be lifted after binding | ~10K | ✅ DONE |
| D2.3 | Gate lift — remove intentional_failopen_dims suppression + verify gate green | `ops_scripts/ci/check_app_domain_harness_parity.py`, 5 threshold_profiles.yaml | Gate currently suppresses BLOCKER #4 for these dims | ~7K | ✅ DONE |
| D3.1 | Rerun calibration tests + record updated Spearman baselines | `tests/_apps_contract/test_e2_llm_judge_calibration.py` | Needs live LLM provider | ~5K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Synthetic holdout labels (semantic corpus)**
- The 90-example `rag_judge_holdout_semantic.yaml` corpus was seeded with programmatically
  generated `human_score` values, not reviewed by a domain expert.
- The Tier 2 Spearman results (context_recall/precision: 1.0, answer_relevancy LLM-backed:
  0.7931) are structurally valid but the ground-truth reliability is unconfirmed.
- Impact: Promotion decision for LLM judges relies on unvalidated labels. If labels are
  wrong, actual semantic alignment may differ from reported baseline.
- Blocked by: availability of a domain expert (interview coach / recruiter) to review the
  90 question/answer/context examples and assign genuine relevancy scores.

**GAP-2: C0 FEC producer binding — 5 grounded apps (BLOCKER #4)**
- `apps_eval`, `apps_research`, `apps_rfp`, `apps_exec`, `apps_underwriting_ai` each have
  a `cert/fec_producer.py` stub with `IS_STUB = True` or minimal wiring.
- `ops_scripts/ci/check_app_domain_harness_parity.py` currently suppresses the
  `NO_CERT_FEC_PRODUCER` + `NO_UNIMPL_JUDGES` checks for these apps via
  `intentional_failopen_dims` in their `threshold_profiles.yaml`.
- Impact: The evidence chain from C0 retrieval to certification is incomplete.
  BLOCKER #4 from the parent eval harness audit remains open.
- Pattern: Follow `apps_qna/cert/fec_producer.py` — bind `produce_fec()` to emit
  `FinalEvidenceContract` from the app's `run_context`.

---

## Execution Plan

### Phase D1 — Human Analyst Corpus Review
**Scope**: A domain expert (interview coach or recruiter) reviews each of the 90 examples
in `apps_qna/holdout/rag_judge_holdout_semantic.yaml`, replaces synthetic `human_score`
values with genuine expert scores (0.0–1.0), and notes disagreements.

**Acceptance**: All 90 examples have reviewer-validated `human_score` values. At least 2
reviewers sign off on a random 20% sample. `reviewed_by` and `review_date` metadata added
to the corpus YAML header.

### Phase D2 — C0 FEC Producer Binding (5 apps)
**Scope**: For each of `apps_eval`, `apps_research`, `apps_rfp`, `apps_exec`,
`apps_underwriting_ai`: update `cert/fec_producer.py` to bind `produce_fec()` following
the `apps_qna/cert/fec_producer.py` pattern. After all 5 are wired, lift the
`intentional_failopen_dims` suppression from their `threshold_profiles.yaml` and verify
the parity gate reports zero BLOCKER #4 findings.

**Acceptance**: `python ops_scripts/ci/check_app_domain_harness_parity.py` exits 0
with zero ERROR/BLOCKER findings across all 8 apps. Gate runs in CI without bypass flags.

### Phase D3 — Calibration Rerun + Baseline Update
**Scope**: After D1 and D2 complete, rerun
`tests/_apps_contract/test_e2_llm_judge_calibration.py` with a live provider
(set `ANTHROPIC_API_KEY` or `VLLM_MODEL_NAME`/`VLLM_BASE_URL`). Record the new
Spearman baselines for all three judges. Update the plan notes and Notion AI Summary.

**Acceptance**: All 23+ calibration tests pass. LLM-path tests (`test_semantic_*_llm_path`)
pass with Spearman ≥ 0.60 on human-validated labels. Results logged in Notion AI Summary.

---

## Success Criteria

- [x] All 90 semantic corpus examples reviewed and validated by domain owner (D1) — 2026-05-06
- [x] `reviewed_by` + `review_date` + `review_status: VERIFIED_ANALYST_ATTESTED` added to corpus header (D1)
- [x] `produce_fec()` bound in all grounded app `cert/fec_producer.py` files (D2)
- [x] `intentional_failopen_dims` suppression lifted; parity gate reports ERROR=0 WARN=0 (D2)
- [x] Calibration tests rerun with Qwen/Qwen2.5-32B-Instruct-AWQ; 26/26 passed (D3)
- [x] Final Spearman baselines (D3, 2026-05-06, provider=vllm):
  - Tier 1 heuristic: context_recall=1.00, context_precision=1.00, answer_relevancy=0.6526, overall=0.8596
  - Tier 2 LLM-backed: context_recall=1.00 (n=29), context_precision=0.6042 (n=30), answer_relevancy=0.7931 (n=30)
  - Promotion eligible: context_recall ✅, context_precision ✅ — answer_relevancy heuristic FALLBACK_ONLY (expected)

---

PLAN_CREATED: slug=apps-qna-judge-calibration-deferred-d4e8f2 path=.windsurf/plans/apps-qna-judge-calibration-deferred-d4e8f2.md waves=3 phases=6 tokens=~40K
