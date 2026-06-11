---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-qna-remaining-e1e2e3e5-54b6c7.md'
original_relative_path: 'apps-qna-remaining-e1e2e3e5-54b6c7.md'
source_sha256: e6ae6c91d1bfe3a80872553f6629906e7a925c925d20faaffb69cf513cf08d75
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-remaining-e1e2e3e5-54b6c7
plan_type: deferred_scope
parent_plan: apps-qna-deferred-e5-f7a2b1
dependencies: apps-qna-e1-index-populate-d4366e (index populated)
---

# apps_qna — Remaining E1/E2/E3/E5 Deferred Scope

Deferred implementation work from parent plan `apps-qna-deferred-e5-f7a2b1`.
E4 is complete. E1 index is populated. This plan covers the actual implementation
of C0 retrieval wiring, LLM judges, provider dispatch, and CI gates.

**Parent Plan**: `.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md`  
**Index Population**: `.windsurf/plans/apps-qna-e1-index-populate-d4366e.md` (Complete)  
**Created**: 2026-05-05

---

## Completed Prerequisites

| Prerequisite | Status | Reference |
|--------------|--------|-----------|
| E4: Exit-eval hook + UWG | ✅ DONE | `apps_qna/live_interview_runtime.py` |
| E1 Index: BGE-M3 populated | ✅ DONE | `C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\` |
| BGE-M3 embedder | ✅ DONE | `tools/embedders/bge_m3_embedder.py` |
| CI index gate | ✅ DONE | `ops_scripts/ci/check_apps_qna_c0_index.py` |

---

## Remaining Deferred Waves

| Wave | Focus | Est. Tokens | Status | Dependencies |
|------|-------|-------------|--------|--------------|
| E1.1/E1.2 | C0 adapter wiring (replace stub fetcher) | ~25K | 🔲 TODO | Index populated ✅ |
| E2 | Production LLM judges (3 RAG judges) | ~40K | 🔲 TODO | Model credentials, holdout corpus |
| E3 | Provider SDK dispatch | ~30K | 🔲 TODO | E1 complete |
| E5 | SSOT enforcement gates (CI) | ~15K | ✅ DONE | None — independent |

---

## Deferred Items

### E1: Real C0 Vector-Store Retrieval (~25K remaining)

**Current State**: Index is populated with 110 BGE-M3 embeddings. C0 adapter still uses stub fetcher.

**E1.1: Replace stub fetcher in c0_adapter.py**
- File: `apps_qna/c0_adapter.py` lines 96–100
- Current: `_stub_fetch` returns empty `CandidateEvidencePool`
- Needed: Wire real BGE-M3 retrieval from `apps_qna_interview_cards` index
  - Use `tools.embedders.get_embedder()` for query embedding
  - Query `C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\index.json`
  - Return top-k cards as `CandidateEvidencePool`
- Impact: Changes `evidence_sufficiency` from `template_only` → `grounded`

**E1.2: Wire grounded evidence path**
- Update `FinalEvidenceContract` population to set `grounded=True` when C0 returns results
- File: `apps_qna/c0_adapter.py` → `resolve_fec()` integration
- Impact: Enables real `evidence_sufficiency='grounded'` paths in eval pipeline

### E2: Production LLM Judges (~40K)

**Blockers**: Model credentials, holdout corpus with human judgments

**E2.1: context_recall_judge.py — LLM call**
- File: `apps_qna/engines/judges/context_recall_judge.py`
- Current: Deterministic heuristic `min(len(retrieved ∩ required) / len(required), 1.0)`
- Needed: LLM evaluation via `QnaProviderContext.dispatch()`
- Prompt: "Does retrieved context contain necessary evidence to answer?"

**E2.2: context_precision_judge.py — LLM call**
- File: `apps_qna/engines/judges/context_precision_judge.py`
- Current: Overlap-score heuristic
- Needed: LLM evaluation of precision — relevance vs noise

**E2.3: answer_relevancy_judge.py — LLM call**
- File: `apps_qna/engines/judges/answer_relevancy_judge.py`
- Current: Keyword-overlap heuristic
- Needed: LLM evaluation of answer responsiveness

**E2.4: Judge calibration against holdout corpus**
- Run judges against holdout partition with human judgments
- Establish Spearman rank-correlation baseline ≥ 0.80
- File: `tests/_apps_contract/test_e2_judge_calibration.py`

### E3: Live Provider SDK Dispatch (~30K)

**Blockers**: E1 complete (C0 retrieval sources needed)

**E3.1: Wire QnaProviderContext.dispatch()**
- File: `apps_qna/integrations/provider_adapter.py`
- Current: `has_model()` returns True but no actual dispatch
- Needed: Implement `dispatch(prompt: str) -> str` calling model via `agentic_core` SDK
- Fail-soft: return `""` if model unavailable

**E3.2: Wire PA adapter to provider**
- File: `apps_qna/card_context/pa_adapter.py`
- Current: `dispatchable=True` validates context but doesn't call model
- Needed: Call `QnaProviderContext.dispatch()` when `dispatchable=True`
- Return model output as `PAAdapterResult.model_output`

### E5: SSOT Enforcement Gates (~15K)

**No blockers — can be done independently**

**E5.1: Promote config_inventory scan to CI gate**
- Create `ops_scripts/ci/check_apps_qna_config_drift.py`
- Run `scan_config_inventory()`, fail on `drift_violations`
- Check `policy_hash`-bearing configs have `version` and `status`

**E5.2: Spine alignment gate**
- Add `check_spine_alignment()` to apps-spine-coverage CI scanner
- File: `tools/analysis/apps_spine_coverage.py`
- Fail on unknown route types

**E5.3: Holdout partition lock**
- Freeze `salt` in `apps_qna/config/domain_contract/eval_rubrics.yaml`
- Add CI check alerting on `holdout_salt` changes
- Prevents corpus-reassignment risk

---

## Implementation Notes

**Critical Path**:
```
E1.1/E1.2 (C0 wiring) → E3 (provider dispatch) → E2 (LLM judges with real context)
```

**Independent Track**: E5 (CI gates) can proceed anytime — no dependencies.

**E2 Blockers**:
- LLM provider credentials (GPT-4/Claude API keys in CI/production)
- Holdout corpus with human judgments for calibration

**Risk**: E2 requires Spearman ≥ 0.80 calibration. If human judgments unavailable, may need to defer E2 indefinitely or use reference-based metrics (BLEU/ROUGE) as interim.

---

## Success Criteria

- [ ] C0 adapter calls real vector store (evidence_sufficiency = "grounded")
- [ ] `context_recall_judge.py` makes LLM calls (not heuristic)
- [ ] `context_precision_judge.py` makes LLM calls
- [ ] `answer_relevancy_judge.py` makes LLM calls
- [ ] Judge Spearman calibration ≥ 0.80 on holdout corpus
- [ ] `QnaProviderContext.dispatch()` makes real model calls
- [ ] PA adapter triggers model execution when `dispatchable=True`
- [x] config_inventory drift scan wired into CI (ops_scripts/ci/check_apps_qna_config_drift.py) 
- [x] spine_alignment check wired into apps-spine-coverage CI scanner 
- [x] holdout_salt frozen in eval_rubrics.yaml with change-detection gate 

---

## Non-Goals

- Do NOT implement E2 without holdout corpus + human judgments
- Do NOT modify `healing_contexts` index (leave untouched)
- Do NOT create new evaluation rubrics (use existing 22-card structure)

---

PLAN_CREATED: slug=apps-qna-remaining-e1e2e3e5-54b6c7 path=.windsurf/plans/apps-qna-remaining-e1e2e3e5-54b6c7.md waves=4 phases=11 tokens=110K
