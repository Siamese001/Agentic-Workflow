# fact_vec Pipeline Gap Remediation

Remediates all 7 architectural gaps in the `fact_vec` ingestion → enrichment → storage → retrieval → eval pipeline identified during investigation.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| **W1** | P1–P2 | Production correctness: wire SemanticEnricher + fix dense search singleton | ~8K | `SemanticEnricher` API stable | 🔲 TODO | GAP-1, GAP-7 closed; existing e2e tests green |
| **W2** | P3 | Consolidate duplicate SemanticEnricher implementations | ~5K | `tools/scripts/enrich_embeddings.py` can be archived | 🔲 TODO | GAP-2 closed; single canonical class |
| **W3** | P4–P5 | Wire live eval + add fact_vec drift detection | ~6K | SQLite artifacts accessible at runtime | 🔲 TODO | GAP-3, GAP-5 closed; eval metrics emitted on search |
| **W4** | P6–P7 | Unit test suite + orphaned script clean-up | ~9K | pytest infra stable | 🔲 TODO | GAP-4, GAP-6 closed; ≥90% unit coverage on changed files |

**Total: ~28K tokens across 4 waves, all 🟢 GREEN**

---

## Gap Register (recap)

| # | Gap | Severity |
|---|-----|----------|
| GAP-1 | `SemanticEnricher.to_enriched_text()` never called in indexing path — raw text embedded instead of enriched payload | **High** |
| GAP-2 | Two incompatible `SemanticEnricher` classes: LLM-based in `agentic_core/` and regex-based in `tools/scripts/` | **High** |
| GAP-3 | `RetrievalEvalRegistry.evaluate_retrieval()` never called from `HybridRetriever` | **Medium** |
| GAP-4 | `tools/scripts/enrich_embeddings.py` writes to `agentic_best_practices_semantic` collection that nothing reads | **Medium** |
| GAP-5 | ChromaDB ↔ SQLite L4D `fact_vec` drift has no detection or repair | **Medium** |
| GAP-6 | Zero unit tests for `ChunkManifestRegistry`, `GraphAwareIndexer._create_enriched_manifest`, `SemanticEnricher.to_enriched_text`, `RetrievalEvalRegistry` | **Medium** |
| GAP-7 | Default `HybridRetriever` singleton uses `_InMemoryVectorStore` which ignores query embedding — dense search is a no-op | **Low** |

---

## Execution Plan

### Wave 1 — Production Correctness

#### P1 — Wire SemanticEnricher into GraphAwareIndexer (GAP-1)
**Scope**: `agentic_core/L3_orchestration/reasoning/engines/graph_aware_indexer.py`

- Lazy-import `SemanticEnricher` from `agentic_core.knowledge.enrichment.semantic_enricher` (pattern already used in file)
- In `_create_enriched_manifest`: call `SemanticEnricher().enrich(content)` → `SemanticKnowledgeObject` → `.to_enriched_text()` → pass enriched text to embedding generator instead of raw `content`
- Populate manifest `title`, `summary`, `key_concepts` from the `SemanticKnowledgeObject` fields
- Fail-open: if enrichment raises, log warning and fall back to raw content

**Files**: `graph_aware_indexer.py`

**Acceptance**: Manifests have non-empty `title` and `key_concepts` populated from enrichment, not empty defaults.

---

#### P2 — Fix No-Op Dense Search Singleton (GAP-7)
**Scope**: `agentic_core/L2_execution/config/hybrid_retriever_config.py`

- `_InMemoryVectorStore.similarity_search` currently ignores `query_embedding`; implement cosine similarity ranking over stored docs
- Unblocks dense retrieval in test/dev environments without requiring live ChromaDB

**Files**: `hybrid_retriever_config.py`

**Acceptance**: `similarity_search(query_embedding=[...], top_k=3)` returns docs ranked by cosine similarity, not insertion order.

---

### Wave 2 — Dedup SemanticEnricher

#### P3 — Consolidate Duplicate SemanticEnricher (GAP-2 + GAP-4)
**Scope**: `tools/scripts/enrich_embeddings.py`, `agentic_core/knowledge/enrichment/semantic_enricher.py`

- Add `enrich_chunk(raw_text, metadata) -> dict` adapter method to the canonical `SemanticEnricher` so `SemanticPipeline` can use the same interface
- Rename `tools/scripts/enrich_embeddings.py::SemanticEnricher` → `_LegacyRuleBasedEnricher` (private, deprecated)
- Update `SemanticPipeline` to delegate to `agentic_core.knowledge.enrichment.semantic_enricher.SemanticEnricher`
- Archive the old rule-based class to `tools/archive/enrich_embeddings_legacy.py`

**Files**: `enrich_embeddings.py`, `semantic_enricher.py`, new `tools/archive/enrich_embeddings_legacy.py`

**Acceptance**: `grep -r "class SemanticEnricher" agentic_core/ tools/scripts/` returns exactly 1 result.

---

### Wave 3 — Live Eval Wiring + Drift Detection

#### P4 — Wire RetrievalEvalRegistry into HybridRetriever (GAP-3)
**Scope**: `agentic_core/L2_execution/config/hybrid_retriever_config.py`

- After `hybrid_search()` returns results, call `get_global_eval_registry().evaluate_retrieval(trace_id, query, retrieved_chunk_ids, relevant_chunk_ids=[], eval_mode="shadow")`
- Ground truth unavailable at runtime → use shadow mode with empty `relevant_chunk_ids`; completeness/fragmentation triggers can still fire on retrieved set shape
- Non-blocking: wrapped in `try/except`, failure logged but not raised

**Files**: `hybrid_retriever_config.py`, `retrieval_eval_registry.py` (read-only)

**Acceptance**: After `hybrid_search(...)`, `RetrievalEvalRegistry.get_stats()["total_evaluations"] > 0`.

---

#### P5 — fact_vec Drift Detection (GAP-5)
**Scope**: `agentic_core/L4_state/utils/memory/chunk_manifest_registry.py`

- Add `check_drift(chroma_collection) -> list[str]`: compare ChromaDB IDs vs. manifest `chunk_id` set; return orphaned/missing IDs
- Add `verify_fact_vec_hash(manifest) -> bool`: re-hash `fact_vec` and compare to stored `fact_vec_hash`
- Read-only diagnostics only — no auto-repair in this wave

**Files**: `chunk_manifest_registry.py`

**Acceptance**: `check_drift(collection)` returns `[]` when stores are in sync; returns missing IDs when drift is present.

---

### Wave 4 — Unit Tests + Script Clean-Up

#### P6 — Unit Test Suite (GAP-6)
**Scope**: `tests/unit/agentic_core/` (4 new test files)

| Test File | Tests | Covers |
|-----------|-------|--------|
| `test_chunk_manifest_registry.py` | 10 | `store_manifest`/`_row_to_manifest` round-trip, `fact_vec_hash` integrity, `check_drift`, `verify_fact_vec_hash` |
| `test_graph_aware_indexer_manifest.py` | 8 | `_create_enriched_manifest` with/without embedding, enricher mock, `fact_vec_hash` computation |
| `test_semantic_enricher.py` | 8 | `to_enriched_text()` correctness, mock LLM, cache hit/miss |
| `test_retrieval_eval_registry.py` | 8 | `compute_metrics` edge cases, store/retrieve round-trip, `evaluate_answer` F1 update |

**Acceptance**: `pytest tests/unit/agentic_core/ -x` passes; ≥90% coverage on all files modified in W1–W3.

---

#### P7 — Archive Orphaned Script (GAP-4 cleanup)
**Scope**: `tools/scripts/enrich_embeddings.py` (after P3 consolidation)

- Move to `tools/archive/enrich_embeddings_standalone.py` with deprecation header
- Add `# ARCHIVED: superseded by agentic_core.knowledge.enrichment.semantic_enricher` comment block

**Files**: `tools/scripts/enrich_embeddings.py`, `tools/archive/`

**Acceptance**: No active production import of `tools.scripts.enrich_embeddings`.

---

## Micro-Wave Breakdown

```
W1 ─ P1
  μ1a  Re-read graph_aware_indexer.py lines 140-295 → confirm exact injection point
  μ1b  Write SemanticEnricher lazy import + call in _create_enriched_manifest
  μ1c  Verify fail-open fallback (try/except + log)
  μ1d  pytest tests/e2e/retrieval_layers/test_graphrag_e2e.py -x

W1 ─ P2
  μ2a  Implement cosine similarity in _InMemoryVectorStore.similarity_search
  μ2b  pytest tests/e2e/retrieval_layers/test_graphrag_hardened.py -x

W2 ─ P3
  μ3a  Add enrich_chunk() adapter to canonical SemanticEnricher
  μ3b  Rename legacy class → _LegacyRuleBasedEnricher; update SemanticPipeline import
  μ3c  Move file to tools/archive/

W3 ─ P4
  μ4a  Add shadow eval call in hybrid_search() (4 lines)
  μ4b  Smoke-test: confirm eval registry population

W3 ─ P5
  μ5a  Add check_drift() to ChunkManifestRegistry
  μ5b  Add verify_fact_vec_hash() to ChunkManifestRegistry

W4 ─ P6
  μ6a  test_chunk_manifest_registry.py (10 tests)
  μ6b  test_graph_aware_indexer_manifest.py (8 tests)
  μ6c  test_semantic_enricher.py (8 tests)
  μ6d  test_retrieval_eval_registry.py (8 tests)
  μ6e  pytest --co -q → verify collection
  μ6f  pytest tests/unit/agentic_core/ -x --tb=short

W4 ─ P7
  μ7a  Archive script with deprecation header
```

---

## Rules

- **T2 tier**: each phase touches 1–3 files; no new cross-layer imports without lazy-import pattern
- **Constitutional §1**: tests written alongside or before logic changes (P1 and P6 coordinated)
- **No skip**: all new tests must pass unconditionally; no `pytest.mark.skip`
- **Fail-open enrichment** (P1): enrichment errors must never block indexing
- **Archive not delete** (P3, P7): old code to `tools/archive/` per SVP Engineering §9c
- **Read-only diagnostics** (P5): drift detection methods must not mutate state

---

## Rollback Strategy

1. **W1-P1**: `git revert` `graph_aware_indexer.py`; prior behavior (raw text embedding) restored exactly
2. **W2-P3**: restore archived file; repoint `SemanticPipeline` import back to old class
3. **W3-P4**: remove 4-line shadow eval block from `hybrid_search()`; wrapped in try/except so removal is clean
4. **W3-P5**: remove two methods; pure additive, zero behavioral impact
5. **W4-P6/P7**: delete test files and restore archived script

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| GAP-1 closed | Manifests embed enriched text, not raw | `assert manifest.title != ""` in indexer test |
| GAP-2 closed | Single canonical `SemanticEnricher` | `grep -r "class SemanticEnricher" agentic_core/ tools/scripts/` → 1 result |
| GAP-3 closed | Eval metrics emitted after search | `get_stats()["total_evaluations"] > 0` after one search |
| GAP-4 closed | No orphaned semantic collection writes | Archive confirmed; `grep -r "enrich_embeddings" agentic_core/` → 0 results |
| GAP-5 closed | Drift detection present | `check_drift([])` returns `[]`; `verify_fact_vec_hash(manifest)` returns `True` |
| GAP-6 closed | 34 unit tests green | `pytest tests/unit/agentic_core/ -x` passes |
| GAP-7 closed | Dense search ranks by cosine | Top result changes when query vector changes |
