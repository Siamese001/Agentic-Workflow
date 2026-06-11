---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hybrid-rag-bm25-hardening-bf7f69.md'
original_relative_path: 'hybrid-rag-bm25-hardening-bf7f69.md'
source_sha256: e89f75eab68739a8362100b0c73d1c5a85a1297781c181ab213d989f76a67407
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hybrid RAG (BM25 Keyword) Hardening

Consolidates the fragmented BM25 implementations, wires the unified hybrid retriever into both RAG orchestrators, and proves RRF fusion quality with deterministic tests.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State (AST Scan Findings)

### Files in scope
| File | Role |
|------|------|
| `agentic_core/L4_state/memory/bm25_store.py` | `Bm25Store` + `get_bm25_store()` singleton |
| `agentic_core/L2_execution/config/hybrid_retriever_config.py` | `HybridRetriever` + `ASTAwareTokenizer` + RRF |
| `apps_shared/types/hybrid_scorer_types.py` | `BM25Scorer`, `ScoringWeights` (standalone copy) |
| `agentic_core/knowledge/engine/rag_orchestrator.py` | `self.Bm25Store = None` — dead BM25 path |
| `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | `self.bm25_store = None` — dead BM25 path |
| `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py` | No BM25 reference |

### Critical Gaps Found

**Gap 1 — Two separate BM25 implementations (CONSOLIDATION RISK)**
- `bm25_store.py`: `Bm25Store` uses `rank_bm25.BM25Okapi` directly, simple whitespace tokenization.
- `apps_shared/types/hybrid_scorer_types.py`: `BM25Scorer` is a bespoke reimplementation (no `rank_bm25` dependency) with `k1=1.2, b=0.75` parameters.
- `hybrid_retriever_config.py`: third variant — uses `rank_bm25.BM25Okapi` with `ASTAwareTokenizer`.
Three divergent implementations; no single authority.

**Gap 2 — `Bm25Store` uses naïve whitespace tokenization**
`_build_index()` tokenizes with `doc["text"].lower().split()`. No identifier splitting, no stop words, no AST awareness. Misses code symbols entirely.

**Gap 3 — BM25 never connected in any production RAG path**
All three orchestrators have `bm25_store = None` or `Bm25Store = None`. BM25 keyword search has never run in production.

**Gap 4 — No score normalization before RRF**
`HybridRetriever.reciprocal_rank_fusion()` uses raw BM25 scores (unbounded float) and dense scores (0–1 cosine). RRF ranks are correct but `RetrievalResult.score` field is updated in-place to the RRF score, discarding original scores.

**Gap 5 — `HybridRetriever` requires injected `vector_store` + `guardrail`**
Constructor signature: `HybridRetriever(vector_store, guardrail)`. No defaults, no factory. Impossible to instantiate without knowing external dependency shape.

**Gap 6 — `asyncio.create_task` in `HybridRetriever.__init__`**
`self._init_task = asyncio.create_task(self._load_or_rebuild_local_index())` fails if called outside an async context (e.g., in sync init path or tests). Raises `RuntimeError: no current event loop`.

**Gap 7 — No deterministic test proving BM25 contributes to final results**

---

## Phase 1 — Consolidate BM25 Implementations (Wave 1)

**Scope:** `bm25_store.py`, `apps_shared/types/hybrid_scorer_types.py`

**Wave 1-A: Upgrade `Bm25Store` tokenizer to `ASTAwareTokenizer`**
- Import `ASTAwareTokenizer` from `hybrid_retriever_config.py` (or move it to a shared util: `agentic_core/utils/ast_tokenizer_util.py`).
- Replace `doc["text"].lower().split()` in `_build_index()` and `query()` with `ASTAwareTokenizer.tokenize_code(doc["text"])` and `ASTAwareTokenizer.tokenize_query(query)` respectively.
- Keep `rank_bm25.BM25Okapi` as the engine (already the right choice; `BM25Scorer` in `hybrid_scorer_types.py` is demoted to a legacy type).

**Wave 1-B: Deprecate `BM25Scorer` in `hybrid_scorer_types.py`**
- Add `DeprecationWarning` to `BM25Scorer.__init__` pointing to `Bm25Store`.
- Keep the class to avoid breaking imports; do not delete.

**Acceptance criteria:**
- `Bm25Store.query("def compute_heal_confidence")` returns the file containing that function name in top-3.
- `BM25Scorer()` emits `DeprecationWarning`.
- `ASTAwareTokenizer` lives in single canonical location.

---

## Phase 2 — Fix `HybridRetriever` Async Init + Wire Singleton (Wave 2)

**Scope:** `hybrid_retriever_config.py`

**Wave 2-A: Remove `asyncio.create_task` from `__init__`**
- Replace `self._init_task = asyncio.create_task(...)` with a lazy init pattern:
  - `self._index_initialized = False`
  - First call to `hybrid_search()` checks flag; if False, calls `await self._ensure_index()`.
- This allows synchronous construction without an event loop.

**Wave 2-B: Factory with injectable vector store**
- Add `HybridRetrieverFactory.from_in_memory_store()` that constructs `HybridRetriever` with:
  - `vector_store = InMemoryVectorStore()` (from `L4_state/memory/in_memory_vector_store.py`)
  - `guardrail = NoOpGuardrail()` (new stub: `rerank_documents` returns input unchanged)
- Expose `get_hybrid_retriever()` singleton (same pattern as `get_bm25_store()`).

**Acceptance criteria:**
- `HybridRetriever(...)` constructable in synchronous test context without `asyncio.run`.
- `get_hybrid_retriever()` returns same instance on repeated calls.
- `NoOpGuardrail.rerank_documents(candidates, query)` returns `candidates[:top_k]` unchanged.

---

## Phase 3 — Wire BM25 + Hybrid Retriever into All Orchestrators (Wave 3)

**Scope:** `rag_orchestrator.py` (knowledge/engine), `SovereignRAGManagerAgent.py`, `sovereign_rag_orchestrator.py` (L3)

**Wave 3-A: Wire `Bm25Store` singleton**
In each orchestrator `__init__`:
```python
from agentic_core.L4_state.memory.bm25_store import get_bm25_store
self.bm25_store = get_bm25_store()
```
Replace all `if self.Bm25Store:` / `if self.bm25_store:` guards — now always truthy.

**Wave 3-B: Wire `HybridRetriever` for dense+sparse in `SovereignRagOrchestrator` (knowledge/engine)**
- Replace the inline `_InMemVectorStore` and separate `_BGEEmbedder` with `get_hybrid_retriever()`.
- Route all `retrieve()` calls through `hybrid_retriever.hybrid_search(query, top_k)`.
- RRF fusion is handled inside `HybridRetriever.reciprocal_rank_fusion()`.

**Acceptance criteria:**
- Integration test: ingest 3 documents, query with keyword present in only one → BM25 doc appears in top-3.
- Integration test: query with semantic match only → dense result appears in top-3.
- Integration test: document present in both lists → appears once (deduplication).

---

## Phase 4 — Score Normalization + Deterministic RRF Test (Wave 4)

**Wave 4-A: Preserve original scores in `RetrievalResult`**
- Add `original_score: float` field alongside `score` (which becomes RRF score).
- Prevents loss of raw BM25/dense scores for downstream quality evaluation.

**Wave 4-B: Deterministic RRF correctness test**
Invariants to prove:
- Identical inputs → identical ranked output (no randomness).
- Doc in rank-1 of both lists scores higher than doc in rank-2 of one list.
- RRF constant `k=60` produces expected formula: `1/(60+1) + 1/(60+1) = 0.032...` for dual-rank-1.
- Tie-break is stable: deterministic sort on `doc_id` when RRF scores equal.

**Wave 4-C: Context budget enforcement**
- Before returning from `hybrid_search()`, trim results so total token count ≤ configured budget.
- Use `len(text.split()) * 1.3` as token estimate (fast, no tokenizer dependency).

**Evidence file:** `docs/reports/sub/phase_hybrid_rag_bm25_evidence.md`

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `rank_bm25` import fails in CI (not installed) | Low | Already required in `.[infra]` extras; CI must install infra deps |
| ASTAwareTokenizer raises `SyntaxError` on non-Python docs | Low | Fallback to regex path already in `tokenize_code` |
| BM25 index rebuild latency on first call | Medium | Lazy rebuild + JSON cache at `L4_state/memory/.sovereign_local_index.json` |
| In-place `score` mutation in `reciprocal_rank_fusion` | Medium | Phase 4-A adds `original_score` before mutation |
| `NoOpGuardrail` masking reranking issues in tests | Low | Integration tests must assert BM25 + dense both contribute |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

