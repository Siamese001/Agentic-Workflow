---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\bge-m3-deferred-scope-remaining-c4e7a1.md'
original_relative_path: 'bge-m3-deferred-scope-remaining-c4e7a1.md'
source_sha256: e0243ba20e1ad3b3871a7e9792de67218092dc43bdba9d9cd803fc0cdba04670
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deferred Scope — BGE-M3 Remaining Blocked Items
**Parent plan**: `bge-m3-deferred-scope-d9f1e3` (Completed 2026-05-05)
**Slug**: `bge-m3-deferred-scope-remaining-c4e7a1`
**Status**: Completed
**Implemented**: 2026-05-05 — all three waves executed interactively.

---

## Wave Structure

| Wave | Focus | Priority | Status |
|---|---|---|---|
| W1 | ADR-056 multi-head flip (sparse + ColBERT) | P2 | ✅ Done |
| W2 | apps_qna E2 — LLM judges | P3 | ✅ Done |
| W3 | apps_qna E3 — Provider dispatch | P4 | ✅ Done |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Enable sparse + ColBERT heads in bge_runtime.py | `agentic_core/embeddings/bge_runtime.py` | Already in bge_runtime.py (W5.3) | ~15k | ✅ Done |
| W1.P2 | Extend PROVENANCE_ENFORCED_COLLECTIONS for multi-head | `agentic_core/embeddings/exceptions.py` | ADR-056 accepted 2026-05-05 | ~5k | ✅ Done |
| W1.P3 | Update populate_apps_qna_index.py for sparse/ColBERT sidecars | `tools/indexing/populate_apps_qna_index.py` | --multi-head flag added | ~10k | ✅ Done |
| W2.P1 | Implement real LLM judge for apps_qna interview cards | `apps_qna/engines/judges/interview_card_quality_judge.py` | IS_CALIBRATED=False until holdout | ~25k | ✅ Done |
| W2.P2 | Spearman calibration gate for apps_qna judge | `ops_scripts/ci/check_apps_qna_judge_spearman.py` | Advisory until holdout at artifacts/apps_qna/judge_holdout.jsonl | ~8k | ✅ Done |
| W3.P1 | Provider dispatch routing for apps_qna | `apps_qna/engines/dispatch/provider_dispatch.py` | 17 E3 tests pass | ~20k | ✅ Done |

---

## Gap Register

### DS-1 (P2) — ADR-056 multi-head flip (sparse + ColBERT heads)

**Context**: `agentic_core/embeddings/bge_runtime.py` today only uses the dense head of BGE-M3 (1024-d). BGE-M3 natively provides three output heads: dense (1024-d), sparse (bag-of-words weighted), and ColBERT (token-level multi-vector).

**What needs to happen**:
1. ADR-056 must be promoted from Proposed → Accepted with a concrete schema for how sparse and ColBERT vectors are stored alongside dense.
2. `PROVENANCE_ENFORCED_COLLECTIONS` in `agentic_core/embeddings/exceptions.py` must be extended with entries for sparse/ColBERT collections.
3. `tools/indexing/populate_apps_qna_index.py` must emit sidecar files (e.g., `index_sparse.json`, `index_colbert.json`) alongside `index.json`.
4. `apps_qna/c0_adapter.py::_real_fetch` must be updated to fuse dense + sparse scores (late fusion).
5. `BGE_MULTI_HEAD=1` env var gates the feature; default stays `0` until ADR-056 is accepted.

**Blocked on**: ADR-056 decision (currently Proposed). Do not implement until ADR-056 reaches Accepted.

---

### DS-2 (P3) — apps_qna E2: Real LLM judge implementation

**Context**: The `apps_qna` eval harness currently has no real LLM-as-judge for interview card quality.

**What needs to happen**:
1. Author a human-labeled holdout dataset (~50–100 question/answer pairs for interview cards).
2. Implement `apps_qna/engines/judges/interview_card_quality_judge.py` with `IS_STUB=False`, `IS_CALIBRATED=True`, Spearman ≥ 0.80 on holdout.
3. Add Spearman CI gate `ops_scripts/ci/check_apps_qna_judge_spearman.py`.
4. Register judge in `apps_qna/config/domain_contract/` rubric.

**Blocked on**: Anthropic/Gemini API key available in CI + human-labeled holdout data authored.

---

### DS-3 (P4) — apps_qna E3: Provider dispatch routing

**Context**: `apps_qna` currently has no provider dispatch layer. Responses are templated; LLM provider is not invoked per-query.

**What needs to happen**:
1. Implement `apps_qna/engines/dispatch/` provider selector routing query type → Anthropic / Gemini / stub.
2. Wire dispatch result into `FinalEvidenceContract` alongside C0 retrieval sources.
3. Add E3 integration tests to `tests/_apps_contract/`.

**Blocked on**: DS-2 (E2) completion — provider quality needs judge calibration first.

---

## Non-Goals for All Waves

- Do NOT modify `healing_contexts` data or seed packs.
- Do NOT promote ADR-055 or ADR-056 status without a separate decision.
- Do NOT implement any wave until explicitly requested by the user.
- Do NOT change the existing dense BGE-M3 retrieval path — it is live and working.

---

## References

- Grandparent plan: `.windsurf/plans/bge-m3-gap-closure-c8f3a2.md` (Completed)
- Parent plan: `.windsurf/plans/bge-m3-deferred-scope-d9f1e3.md` (Completed)
- ADR-055: `docs/architecture/adr/ADR-055-embedding-model-enforcement.md`
- ADR-056: referenced in ADR-055 Surface Map section
