# BGE+FAISS Complete Embedding Implementation Plan

All 30 production gaps across 32 files — derived from codebase scan, `Embedding Lifecycle.md`, and `agentic_process_mapping.md` — with zero remaining OpenAI/Gemini/MiniLM/Pinecone in the embedding lifecycle.

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


## Lifecycle Anchor (from `Embedding Lifecycle.md`)

```
RAW SIGNAL → BGE-m3 EMBED → FAISS INDEX → FAISS SEARCH → ROUTING → HEALING → LEARNING LOOP
```

BGE-m3 is the **only** allowed embedding model. FAISS is the **only** allowed vector store. Pinecone is removed entirely. All embedding instantiation routes through `EmbeddingSovereignAgent` (live) or `EmbeddingServiceFactory` (seed pack).

---

## Gap Count

| Tier | Gaps | Files |
|------|------|-------|
| CRITICAL — lifecycle broken / wrong provider | 18 | 20 |
| HIGH — wrong model / O(N) scan | 8 | 8 |
| MEDIUM — apps layer Pinecone / cleanup | 4 | 4 |
| **TOTAL** | **30** | **32** |

---

## Sprint 1 — Foundation (unblocks everything downstream)

### P10 · `agentic_core/config/core/sovereign_config.py`
Add `DEFAULT_BGE_EMBEDDING_MODEL = "BAAI/bge-m3"` and `EMBEDDING_DIM_BGE = 1024`. Update `DEFAULT_EMBEDDING_MODEL` from `"text-embedding-3-small"`.

### P16 · `agentic_core/L1_cognition/types/memory_types.py`
Change `EMBEDDING_DIMENSION: Final[int] = 1536  # OpenAI ada-002` to `1024  # BAAI/bge-m3`.

### P9 · `agentic_core/mixins/embedding_mixin.py`
Add `"bge-m3"` to `EmbeddingProvider = Literal[...]`. Change both `get_embedding()` and `get_embeddings_batch()` defaults from `provider="gemini"` to `"bge-m3"`.

### P17 · `agentic_core/config/core/gateway_config.py`
Add `"bge-m3"` to `EmbeddingProvider = Literal["gemini", "openai"]`.

### P1 · `agentic_core/config/core/rag_config.py`
Change `model="all-MiniLM-L6-v2"`, `dim=384`, `provider="pinecone"` to `model="BAAI/bge-m3"`, `dim=1024`, `provider="faiss"`.

### P2 · `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`
Change both `get_embedding()` and `get_embeddings_batch()` default `provider="gemini"` to `"bge-m3"`.

---

## Sprint 2 — Broken imports + `embed_text()` bug fixes

### P4 · `agentic_core/utils/meta_learning_storage_util.py`
Fix broken import: `from ...semantic_cache_manager_config` (non-existent) to `from ...semantic_cache_manager import SemanticCacheManager`. `_memory` is currently always `None`; `recall()` and `learn_async()` are dead.

### P7 · `agentic_core/mixins/meta_learning_client_mixin.py`
Fix broken import: `from ...L1_cognition.reasoning.meta_learning_client_types` (non-existent) to `from ...L1_cognition.engines.meta_client import MetaLearningClient`. All agent healing pattern store/recall is inert.

### P15 · `agentic_core/L1_cognition/engines/memory_embedder.py`
`embed_signature()` and `embed_healing_pattern()` call `self._embedding_agent.embed_text(text)` — method does not exist on `EmbeddingSovereignAgent`. Fix to `self._embedding_agent.get_embedding(text, provider="bge-m3")`.

### P8 · `agentic_core/L1_cognition/engines/meta_client.py`
Replace `_initialize_pinecone()` + Pinecone query/upsert with `InMemoryVectorStore`. Fix `_generate_embedding()`: change `embedding_agent.embed_text()` (non-existent) to `embedding_agent.get_embedding(text, provider="bge-m3")`.

---

## Sprint 3 — FAISS sealing + pipeline vectors

### P3 · `agentic_core/L0_routing/scripts/execute_ssot.py`
`add_vectors()` is called but `finalize_build()` is never called — FAISS index unsealed — all searches return nothing. Add `_faiss_store.finalize_build(_faiss_idx)` after `add_vectors()`.

### P6 · `system_learning/pipelines/meta_learning_pipeline.py`
`_generate_vector()` returns `[hash(text) % 1000 / 1000.0, ...]` — 4-dim hash garbage, not real embeddings. Replace with `bmg_embed_text()` for 1024-dim vectors. Wire live FAISS search via `HealingMemoryRetriever`.

---

## Sprint 4 — Semantic cache + RAG ghost module fix

### P5 · `agentic_core/L4_state/memory/semantic_cache_manager.py`
`_init_pinecone()` + `_get_embedding()` uses Google `text-embedding-004` + Pinecone upsert/query. Replace with `InMemoryVectorStore` + `bmg_embed_text()`. Rename stat key `"pinecone_hits"` to `"faiss_hits"`.

### P11 · `agentic_core/L4_state/memory/sovereign_semantic_cache.py`
`__init__` instantiates `PineconeSovereignAgent`. `cache_file()` calls `pinecone.upsert()`. `invalidate()` calls `pinecone.delete()`. Replace with `InMemoryVectorStore` + `bmg_embed_text()`. Note: `agentic_core/interfaces/embeddings.py` `query_similarity()` routes through here.

### P12a · `agentic_core/knowledge/engine/rag_orchestrator.py`
Imports `GeminiEmbedder`, `PineconeVectorStore`, `Bm25Store` from `agentic_core.semantic_memory.*` which does not exist. Falls back silently to `embedder=None`, `vector_store=None` — RAG vector retrieval has never executed. Replace with `EmbeddingSovereignAgent` + `InMemoryVectorStore`.

### P12b · `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py`
Same ghost imports as P12a. Same fix.

---

## Sprint 5 — Governance unlock + retrieval profile

### P13 · `system_learning/engines/retrieval_profile.py`
`create_default()` hardcodes `primary_embedder_id="openai/text-embedding-3-large"`, `embedding_dim=1536`. Entire system learning retrieval layer is locked to OpenAI. Change to `primary_embedder_id="BAAI/bge-m3"`, `embedding_dim=1024`.

### P14 · `system_learning/constraints/config_surfaces.py`
`L1_MODEL_POINTER_CONSTRAINTS["embedding_model"]` allowlist = `{"text-embedding-3-small", "text-embedding-3-large"}`. `EMBEDDING_GOVERNANCE_POINTER["active_embedder_id"]` allowlist = same. BGE is constitutionally blocked by governance. Add `"BAAI/bge-m3"` to both allowlists.

---

## Sprint 6 — Model replacements + O(N) elimination

### H1 · `apps_shared/enforcement/GlobalcacheStrategy.py`
`SimpleEmbedder(model="all-MiniLM-L6-v2")`, `_embedding_dim=384`. `L2VectorStore.search()` uses `np.dot()` O(N) scan. Replace with `bmg_embed_text()` (1024-dim) + `InMemoryVectorStore`.

### H2 · `apps_shared/validators/cache_entry_validator.py`
`ContrastiveSemanticCache(model_name="all-MiniLM-L6-v2")`. `_calculate_similarity()` is O(N) numpy cosine. Default to `"BAAI/bge-m3"`. Replace O(N) with `InMemoryVectorStore`.

### H3 · `agentic_core/L1_cognition/engines/semantic_manager.py`
`EmbeddingProvider.embed()` returns `[0.0] * 384` — dead stub. `VectorIndex.search()` returns first N keys with no similarity. Wire `embed()` to `bmg_embed_text()` (1024-dim). Replace `VectorIndex` with `InMemoryVectorStore`.

### H4 · `system_learning/engines/meta_learning_embedding_service.py`
`_compute_similarities()` is pure-Python O(N) cosine loop. Replace with `LocalFAISSStore` search.

### H5 · `system_learning/engines/openai_embedder.py`
`text-embedding-3-large` (1536-dim) is seed-pack embedder. Dimension mismatch: BGE FAISS indexes at 1024-dim reject 1536-dim vectors. Replace with BGE shim wrapping `bmg_embed_text()` at 1024-dim.

### H6 · `system_learning/engines/seed_embedding_pack_builder.py`
No enforcement that `dimensions == 1024`. Add `assert dimensions == 1024, "BGE-m3 required"` gate.

### H7 · `apps_shared/utils/late_interaction_reranker_util.py`
`model_name="ms-marco-MiniLM-L-6-v2"` hardcoded default. Change to `"BAAI/bge-reranker-v2-m3"`.

### H8 · `system_learning/engines/embedding_service_factory.py`
`retrieve()` uses `np.dot(self._normalized, q_norm)` — O(N) numpy scan over full seed pack. Replace with `faiss.IndexFlatIP`. Seed pack is built at OpenAI 1536-dim and must be rebuilt at BGE 1024-dim (see Seed Pack Rebuild below). Align `replay_key()` manifest defaults.

---

## Sprint 7 — Sub-Atomic Engine (NEW) + Apps layer cleanup

### N1 · `agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py` *(NEW from process map review)*
`get_embedding()` calls `provider="gemini"` and returns `[0.0] * 768` (Gemini 768-dim) on error. This is L3 orchestration — process map stage 8.7 mandate requires BGE. Change to `provider="bge-m3"`, fallback `[0.0] * 1024`. Remove unused `pinecone_index=None` constructor param.

### M1 · `apps_rg/utils/deep_brain_harvester_util.py`
`DeepBrainHarvester` creates Pinecone index at `dimension=1536`. Replace with `LocalFAISSStore` at dim=1024 + `bmg_embed_text()`.

### M2 · `apps_shared/utils/vector_memory_types_util.py`
`VectorMemoryConfig(dimension=1536)`, Pinecone backend. Change `dimension=1024`, replace backend with `InMemoryVectorStore`.

### M3 · `apps_shared/validators/knowledge_result_validator.py`
`L5ConsolidatedKnowledge(pinecone_client=...)`. Replace with `InMemoryVectorStore`, dim=1024.

### M4 · `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py`
Add `DeprecationWarning` on import once P11 is complete.

---

## Seed Pack Rebuild (prerequisite for H8)

Current pack at `C:/AgenticEmbeddings/seed_packs/healing_contexts/5d94b5b...` is OpenAI 1536-dim.

Required:
1. Run `SeedEmbeddingPackBuilder` with BGE embedder wrapping `bmg_embed_text()` at `dim=1024`.
2. Update `SeedEmbeddingPackManifest.embedding_model_version` to `"BAAI/bge-m3"`.
3. Update `vector_pack_hash` in `config_surfaces.py` `EMBEDDING_GOVERNANCE_POINTER` allowlist to new pack hash.
4. Update hardcoded pack path in `EmbeddingServiceFactory.get_or_disabled()`.

---

## Reference Implementations (already correct — canonical pattern to follow)

- `agentic_core/L2_execution/healers/bmg_embedding_similarity.py` — BGE-m3 via SentenceTransformer, O(N) acceptable for small healer candidate sets
- `agentic_core/L1_cognition/memory/healing_memory_retriever.py` — `bmg_embed_text()` + `LocalFAISSStore.search()` — canonical pattern for all new wiring

---

## Out-of-Scope (confirmed no action)

- `agentic_core/L5_safety/enforcement/vector_healing_strategy.py` — safety guardrail, not embedding lifecycle
- `system_learning/engines/pattern_analysis_engine.py` — `embedder` param exists but new API path is stats-only; no live embedding computation
- `ops_scripts/`, `tools/evidence/` — tooling boundary
- `agentic_core/L2_execution/utils/text_similarity_util.py` — TF-IDF text dedup, not vector retrieval

---

## Process Map Documentation Update (post-code)

`agentic_process_mapping.md` line 60 reads `Embedder: OpenAI text-embedding-3-large (Batch=500, Retry=8)` and line 228 reads `Embedding gen (OpenAI)`. Update to `Embedder: BAAI/bge-m3 (dim=1024)` after code migration.

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

