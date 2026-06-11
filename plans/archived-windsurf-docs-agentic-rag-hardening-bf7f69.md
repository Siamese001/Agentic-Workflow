---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agentic-rag-hardening-bf7f69.md'
original_relative_path: 'agentic-rag-hardening-bf7f69.md'
source_sha256: 0cd0abe2f1cfc14fec449b3e841bbcdf5479f9b217ea2f5ea855f97f16eef201
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic RAG Hardening

Hardens the agentic RAG pipeline so query planning (L1), hybrid retrieval (L2/L3), LLM reranking, and reflection loop are correctly wired, tested, and fail-closed.

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
| `agentic_core/knowledge/engine/rag_orchestrator.py` | `SovereignRagOrchestrator` (knowledge layer) |
| `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py` | L3 self-optimizing RAG |
| `agentic_core/L1_cognition/engines/query_planner.py` | Multi-query, decompose, HyDE |
| `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | Basic RAG agent |
| `agentic_core/L3_orchestration/types/rag_provider_types.py` | `IRagProvider` interface |
| `agentic_core/semantic_memory/embeddings/core_embedder.py` | BGE-m3 embedder (via ghost import) |

### Critical Gaps Found

**Gap 1 — Ghost import in `rag_orchestrator.py` (knowledge/engine) (BREAKING)**
Lines 22–35 import from `agentic_core.semantic_memory.embeddings.core_embedder`. If this module doesn't exist at runtime, the entire RAG orchestrator silently falls back to `ACTION_VERBS={}` and null loaders. The `try/except ImportError` swallows the failure.

**Gap 2 — `self.engine = None` in `SovereignRagOrchestrator` (L3)**
`_llm_rerank()` short-circuits to `candidates[:top_k]` whenever `self.engine is None`.
This means LLM reranking **never runs** in production without an explicit engine injection.

**Gap 3 — `query_planner.py` references undefined types inline**
`query_planner.__init__` uses `SubAtomicEngine` and `semantic_cache` without imports. This is a `NameError` at construction time.

**Gap 4 — `SovereignRAGManagerAgent._fuse_results` is list concatenation only**
Returns `vector + bm25` with no score normalization or RRF. Duplicate chunks silently double-counted.

**Gap 5 — `bm25_store` is never connected in `SovereignRagOrchestrator` (knowledge/engine)**
`self.Bm25Store = None` set in `__init__`. BM25 path is dead code.

**Gap 6 — Async/sync boundary in `get_context_for_task`**
Calls `self.retrieve(Task, ...)` (an `async def`) without `await`. This returns a coroutine object, not results.

**Gap 7 — No agentic reflection loop**
RAG pipeline is single-pass. No iterative query refinement or sufficiency check after retrieval.

**Gap 8 — No integration between `query_planner` (L1) and `SovereignRagOrchestrator` (L3)**

---

## Phase 1 — Fix Breaking Bugs (Wave 1)

**Scope:** `rag_orchestrator.py`, `query_planner.py`, `SovereignRAGManagerAgent.py`

**Wave 1-A: Fix ghost import in `rag_orchestrator.py`**
- Replace the ghost `agentic_core.semantic_memory.embeddings.core_embedder` import with the canonical BGE embedder path (e.g. `agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text`).
- Remove `try/except ImportError` swallowing — let it fail loudly if unavailable.

**Wave 1-B: Fix `query_planner.py` undefined names**
- Add explicit imports for `SubAtomicEngine` (from its canonical L2 path) and replace `semantic_cache` with `SemanticCacheManager` (canonical L4 path).
- Add `__all__` export.

**Wave 1-C: Fix async/sync boundary in `get_context_for_task`**
- Convert `get_context_for_task` to `async def` OR add a synchronous wrapper that calls `asyncio.get_event_loop().run_until_complete(self.retrieve(...))`.
- Add guard: if event loop is running, use `asyncio.ensure_future`.

**Acceptance criteria:**
- `from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator` succeeds without `ImportError`.
- `from agentic_core.L1_cognition.engines.query_planner import query_planner` succeeds.
- `get_context_for_task("test query")` returns a string, not a coroutine.

---

## Phase 2 — BM25 Wiring + RRF Fusion Fix (Wave 2)

**Scope:** `SovereignRAGManagerAgent.py`, `rag_orchestrator.py` (knowledge/engine)

**Wave 2-A: Wire `Bm25Store` into orchestrators**
- In `SovereignRagOrchestrator.__init__` (knowledge/engine): import `get_bm25_store()` and assign `self.Bm25Store = get_bm25_store()`.
- In `SovereignRAGManagerAgent.__init__`: import and wire same singleton.

**Wave 2-B: Replace `_fuse_results` with true RRF**
- Implement `_rrf_fuse(vector_list, bm25_list, k=60)` matching the RRF logic already in `rag_orchestrator.py` (knowledge/engine).
- Replace naïve concatenation in `SovereignRAGManagerAgent._fuse_results`.
- Deduplication: use content hash (already in `HybridRetriever`) before scoring.

**Acceptance criteria:**
- Unit test: `_rrf_fuse([{id:"a", score:0.9}], [{id:"a", score:5.0}], k=60)` → single doc with fused RRF score.
- Deduplication test: same doc in both lists → appears once in fused output.
- BM25 contribution test: query with exact keyword match → BM25 doc appears in top-3.

---

## Phase 3 — LLM Reranking Engine Injection (Wave 3)

**Scope:** `sovereign_rag_orchestrator.py` (L3)

**Wave 3-A: Engine injection protocol**
- Define `RerankEngine` protocol with `async rerank(query, candidates) → list[dict]`.
- Update `SovereignRagOrchestrator.__init__` to accept optional `rerank_engine: RerankEngine | None`.
- When provided, use for `_llm_rerank`; otherwise fall back to score-sorted truncation.

**Wave 3-B: Default rerank engine using Gemini/Qwen**
- Implement `HealingTierRerankEngine` that routes rerank requests through `healing_tier_dispatcher` (LOCAL_AGENT path for small candidate lists, QWEN for large).
- Fail-closed: any exception in reranking → return `candidates[:top_k]` unchanged.

**Acceptance criteria:**
- Test with mock `rerank_engine`: verify engine is called with correct `(query, candidates)`.
- Fallback test: `engine.rerank` raises exception → result is `candidates[:top_k]` with no exception propagation.

---

## Phase 4 — Agentic Reflection Loop (Wave 4)

**Scope:** `sovereign_rag_orchestrator.py` (L3), new `rag_reflection_loop.py`

**Wave 4-A: Sufficiency check after retrieval**
- After initial retrieval, evaluate whether top-k results contain sufficient context for the query.
- Metric: mean cosine similarity of top results to query embedding. If < threshold (0.60), trigger one refinement round.

**Wave 4-B: Query refinement step**
- On low-sufficiency signal: call `query_planner.decompose_query(original_query)` to produce sub-queries.
- Execute retrieval for each sub-query, merge with RRF.
- Max 2 refinement rounds (hard limit, no unbounded recursion).

**Wave 4-C: Integration test — full agentic RAG loop**
- Test: inject query with no strong match → assert refinement triggered once → assert final results better than initial.

**Evidence file:** `docs/reports/sub/phase_agentic_rag_evidence.md`

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Ghost import silently degrades retrieval | High | Phase 1 fix removes swallowing `try/except` |
| LLM reranking latency in hot path | Medium | Max candidate list bounded; fallback to score-sort |
| Reflection loop infinite recursion | Low | Hard cap of 2 iterations with counter guard |
| BM25 index rebuild overhead on startup | Medium | Lazy rebuild only when `.sovereign_local_index.json` absent |

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

