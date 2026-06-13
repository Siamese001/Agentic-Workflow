# ADG-Derived Gap Analysis & Implementation Plan
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## System Learning · BGE Embedding · Semantic Cache · Evaluation Metrics

> **NO CODE CHANGES — PLAN ONLY**
> Updated: 2026-03-12 | ADG Artifacts: `adg_governance_graph_20260312T093508Z.json`,
> `adg_graphsnap_20260312T093508Z.json`, `adg_file_graph_20260312T093508Z.json`,
> `adg_symbol_graph_20260312T093508Z.json`, `adg_test_graph_20260312T093508Z.json`,
> `adg_indexed_20260312T093508Z.sqlite`

---

## 0. ADG Ingestion Summary (All 6 Artifacts)

### Graph Metrics

| Artifact | Key Metric | Value |
|---|---|---|
| `adg_graphsnap` | `call_count` | **15,979** |
| `adg_graphsnap` | `canonical_edge_order` entries | **91,135** |
| `adg_graphsnap` | Dead import edges (total) | **3,306** |
| `adg_governance_graph` | Total governance edges | **1,912** |
| `adg_governance_graph` | Antipatterns | **1,459** |
| `adg_governance_graph` | Layer violations | **224** |
| `adg_file_graph` | Total file edges | **73,558** |
| `adg_symbol_graph` | Total symbol edges | **86,093** |
| `adg_test_graph` | `covers` edges | **2,198** |

### Antipattern Breakdown (Governance Graph)

| Kind | Count |
|---|---|
| `retry_without_backoff` | **804** |
| `silent_exception_swallow` | **577** |
| `global_state_mutation` | **70** |
| `blocking_call_in_async` | **8** |

### Layer Violation Directions (Top 10)

| Direction | Count |
|---|---|
| `L0->L5` | 32 |
| `L_SHARED->L5` | 20 |
| `L_SHARED->L4` | 14 |
| `L2->L5` | 10 |
| `L_SHARED->L0` | 10 |
| `L_SHARED->L2` | 10 |
| `L0->L2` | 9 |
| `L_RUNTIME->L5` | 9 |
| `L3->L5` | 7 |
| `L_SHARED->L_RUNTIME` | 7 |

### Critical ADG Findings for Target Areas

**Graphsnap dead imports** — 67 dead-import edges in `agentic_core/evaluation` alone:
- `evaluation/__init__.py`: 5 dead (runners, schemas packages do not exist)
- `evaluation/metrics/__init__.py`: 11 dead (7 metric files + 3 base classes)
- `evaluation/retrieval/__init__.py`: 51 dead (all retrieval sub-modules not loaded)

**File graph isolation** — Zero cross-boundary import edges:
- **0 files** outside `agentic_core/evaluation` import from it (completely isolated)
- **0 files** outside `system_learning` import from it (not yet integrated into main pipeline)

**Symbol graph** — `bmg_embed_text` has **48 call sites** across 14 files; `LocalFAISSStore` used in **14 files**; `InMemoryVectorStore` still used in **3 files** (must migrate)

**Test graph** — `system_learning` has **121 test files** covering it; `evaluation` has **12 test files** with **36 unique covered symbols**. `evaluation.metrics.completeness_metrics` and `evaluation.config.thresholds` have **zero test coverage**.

**Governance — target area violations** (confirmed from graph):
- `agentic_core/mixins/semantic_cache_mixin.py:44` → `L_SHARED->L4` layer violation
- `system_learning/adapters/system_learning_memory_bridge.py:100` → `L_SL->L4` violation
- `system_learning/engines/shadow_drift_analyzer.py:153` → `L_SL->L6` violation
- `system_learning/engines/stage_barrier_enforcer.py:15` → `L_SL->L5` violation
- `system_learning/pipelines/meta_learning_pipeline.py:971` → `L_SL->L_PG` violation

**CRITICAL: `system_learning/engines/openai_embedder.py` EXISTS** — The graph shows this file contains both `OpenAIEmbedder` and `BGEEmbedder` classes. It has 21 symbol edges. This is an active OpenAI embedding dependency that contradicts BGE exclusivity.

---

## 1. System Learning — Gaps & Plan

### 1.1 Current State (Graph-Confirmed)

- **121 test files** cover `system_learning` — broad coverage.
- **106 uncovered symbol-level items** including: `meta_learning_types` (6), `dampening` validators (4), `pattern_analysis_types` (4), `embedding_corpus_extraction` (4), 3 pipeline modules.
- **0 external consumers** — `system_learning` is not imported by any non-test, non-`system_learning` file in the file graph (completely siloed).
- `agentic_core/L1_cognition/memory/healing_memory_retriever.py` and `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` import `system_learning` types via the ports layer (correct).
- `agentic_core/L0_routing/scripts/execute_ssot.py` imports `system_learning.types.healing_outcome_types.HealingOutcomeEvent` and `LocalFAISSStore` (layer violation: `L0->L_SL`).

### 1.2 Identified Gaps (ADG-Verified)

| ID | Gap | ADG Evidence | Location |
|---|---|---|---|
| SL-01 | `L0Proposer`, `RAGProposer`, `L1Proposer`, `L5Proposer` are Protocol stubs — no concrete implementations registered at runtime | Symbol graph: `meta_learning_pipeline.py` exports these as abstract types only | `meta_learning_pipeline.py` |
| SL-02 | `system_learning` is **completely siloed** — zero non-test files import from it except via ports; evaluation output never feeds back into the pipeline | File graph: 0 cross-boundary import edges | file-graph |
| SL-03 | `EMBEDDING_ENABLED` env-var defaults `"false"` — W2/W4 semantic paths always disabled in production | Symbol graph: `embedding_service_factory.py` reads env only | `embedding_service_factory.py:240` |
| SL-04 | Hardcoded `C:/AgenticEmbeddings/` path in `get_or_disabled()` | Graphsnap dead-import: no SSOT constant for pack root | `embedding_service_factory.py:180` |
| SL-05 | **5 layer violations** in target area confirmed by governance graph | Governance: `L_SL->L4`, `L_SL->L5`, `L_SL->L6`, `L_SL->L_PG` | 5 files listed in §0 |
| SL-06 | **35 antipatterns** in target area: 21 `silent_exception_swallow`, 12 `retry_without_backoff`, 2 `global_state_mutation` | Governance graph | 19 files |
| SL-07 | `openai_embedder.py` contains `OpenAIEmbedder` class alongside `BGEEmbedder` — live OpenAI embedding dependency | Symbol graph: `openai_embedder.py` has 21 edges including `OpenAIEmbedder` | `system_learning/engines/openai_embedder.py` |
| SL-08 | `retrieve()` uses `max_k = 20` placeholder — never reads from `RetrievalProfile.top_k` | Source confirmed in prior session | `embedding_service_factory.py:437` |
| SL-09 | Spot-check baseline never stored in manifest — `_perform_spot_check()` always returns `True` | Source confirmed | `embedding_service_factory.py:393` |
| SL-10 | **106 uncovered symbol-level items** — `meta_learning_pipeline` (3 uncovered), `dampening` validators (4), `embedding_corpus_extraction` (4) have no direct symbol coverage | Test graph | `system_learning/` |
| SL-11 | `execute_ssot.py` (L0) imports `system_learning` types directly — `L0->L_SL` layer violation | File graph | `L0_routing/scripts/execute_ssot.py` |
| SL-12 | `shadow_drift_analyzer.py` imports from L6 (observability) — `L_SL->L6` violation; correct direction should be L6 consuming SL telemetry, not SL importing L6 | Governance graph | `shadow_drift_analyzer.py:153` |

### 1.3 Implementation Steps

| Step | Action | Priority |
|---|---|---|
| SL-S1 | Add SSOT constant `EMBEDDING_PACK_ROOT` to `structure_blueprint_config.py`; replace hardcoded `C:/AgenticEmbeddings/` | HIGH |
| SL-S2 | Remove `OpenAIEmbedder` from `openai_embedder.py`; consolidate to `BGEEmbedder` only; rename file to `bge_embedder.py` | HIGH |
| SL-S3 | Fix 5 layer violations: (a) `semantic_cache_mixin.py:44` — inject L4 via port; (b) `shadow_drift_analyzer.py:153` — emit telemetry via callback not direct L6 import; (c) `stage_barrier_enforcer.py:15` — remove L5 import; (d) `meta_learning_pipeline.py:971` — remove prompt-governance import | HIGH |
| SL-S4 | Fix 21 `silent_exception_swallow` antipatterns in target area — prioritise `system_learning_memory_bridge.py` (5), `config_provider.py` (4), `shadow_drift_analyzer.py` (3) | HIGH |
| SL-S5 | Switch `EMBEDDING_ENABLED` to read from L4 state registry; default to `True` | HIGH |
| SL-S6 | Implement concrete `L0Proposer`, `RAGProposer` bounded by `config_surfaces.py` constraints; wire as defaults in `run_pipeline()` | MEDIUM |
| SL-S7 | Fix `execute_ssot.py` (L0) to import `HealingOutcomeEvent` via L4 state port, not `system_learning` directly | MEDIUM |
| SL-S8 | Wire `evaluation.retrieval.meta_learning_bridge.CompletenessRAGProposer` (confirmed exists in test graph) as the concrete `RAGProposer` implementation | MEDIUM |
| SL-S9 | Add `spot_check_hash` field to seed manifest; populate and validate in `_perform_spot_check()` | MEDIUM |
| SL-S10 | Replace `max_k = 20` with `retrieval_profile.top_k` from active `RetrievalProfile` | MEDIUM |
| SL-S11 | Fix 12 `retry_without_backoff` antipatterns in `signal_grouping_engine.py`, `seed_pack_build_cli.py`, `audit_store.py`, `config_provider.py`, `telemetry_store.py` | LOW |
| SL-S12 | Add direct symbol-level tests for 10 highest-gap modules: `meta_learning_pipeline` (3 uncovered), `dampening` (4), `embedding_corpus_extraction` (4) | LOW |

---

## 2. BGE Embedding Model — Gaps & Plan

### 2.1 Current State (Graph-Confirmed)

- `bmg_embed_text` has **48 call sites** across **14 production + test files** — confirmed canonical.
- Call sites confirmed in: `memory_embedder.py`, `semantic_manager.py`, `meta_client.py`, `healing_memory_retriever.py`, `sovereign_rag_orchestrator.py`, `rag_orchestrator.py`, `SovereignRAGManagerAgent.py`, `semantic_cache_manager.py`, `execute_ssot.py`, `deep_brain_harvester_util.py`, `knowledge_result_validator.py`.
- `LocalFAISSStore` used in **14 files** — well distributed.
- `InMemoryVectorStore` still referenced in **3 files**: `in_memory_vector_cache.py`, `semantic_cache_manager.py`, `sovereign_semantic_cache.py`.
- **CRITICAL:** `system_learning/engines/openai_embedder.py` confirmed present with both `OpenAIEmbedder` and `BGEEmbedder` classes (21 symbol edges).

### 2.2 Identified Gaps (ADG-Verified)

| ID | Gap | ADG Evidence | Location |
|---|---|---|---|
| BGE-01 | `openai_embedder.py` contains `OpenAIEmbedder` — live OpenAI embedding class coexisting with `BGEEmbedder` | Symbol graph: 21 edges, both classes present | `system_learning/engines/openai_embedder.py` |
| BGE-02 | `L1_MODEL_POINTER_CONSTRAINTS["embedding_model"]` still allows `text-embedding-3-small`, `text-embedding-3-large` | Source: `config_surfaces.py:133` | `config_surfaces.py` |
| BGE-03 | `EMBEDDING_GOVERNANCE_POINTER["active_embedder_id"]` still includes non-BGE models | Source: `config_surfaces.py:168` | `config_surfaces.py` |
| BGE-04 | `replay_key()` fallback references `"BAAI/bge-large-en-v1.5"` — wrong model ID | Source: `embedding_service_factory.py:504` | `embedding_service_factory.py` |
| BGE-05 | `InMemoryVectorStore` still present in `semantic_cache_manager.py` and `sovereign_semantic_cache.py` — must migrate to `LocalFAISSStore` | Symbol graph: 3 files still reference `InMemoryVectorStore` | `L4_state/memory/` |
| BGE-06 | `LocalFAISSStore.load_from_disk()` `expected_embedder_id` is optional — callers can silently load mismatched index | Source confirmed | `local_faiss_store.py:584` |
| BGE-07 | No dimension assertion at `add_vectors()` — downstream code does not assert `len(vec) == 1024` before FAISS insert | Cross-cutting | `local_faiss_store.py` |
| BGE-08 | `agentic_core/L2_execution/healers/bmg_embedding_similarity.py` has **2 antipatterns** (governance graph) | Governance: `silent_exception_swallow` at `bmg_embedding_similarity.py` | `bmg_embedding_similarity.py` |
| BGE-09 | No boot-time BGE model checksum verification — `_get_model()` loads via `SentenceTransformer` with no SHA-256 check | Source confirmed | `bmg_embedding_similarity.py:37` |
| BGE-10 | 30 remaining gaps from `bge-faiss-complete-embedding-plan-cd71f9.md` still open — O(N) scan sites in agents not yet replaced | Prior plan | `apps_rg/`, `apps_lic/` |

### 2.3 Implementation Steps

| Step | Action | Priority |
|---|---|---|
| BGE-S1 | Remove `OpenAIEmbedder` from `openai_embedder.py`; retain only `BGEEmbedder`; rename file to `bge_embedder.py`; update all import sites | HIGH |
| BGE-S2 | Remove `text-embedding-3-small` and `text-embedding-3-large` from `L1_MODEL_POINTER_CONSTRAINTS` and `EMBEDDING_GOVERNANCE_POINTER` allowlists | HIGH |
| BGE-S3 | Fix `replay_key()` hf_repo fallback: `"BAAI/bge-large-en-v1.5"` → `"BAAI/bge-m3"` | HIGH |
| BGE-S4 | Migrate `InMemoryVectorStore` in `semantic_cache_manager.py` and `sovereign_semantic_cache.py` to `LocalFAISSStore` with `embedder_id="BAAI/bge-m3"` | HIGH |
| BGE-S5 | Fix 2 `silent_exception_swallow` antipatterns in `bmg_embedding_similarity.py` | MEDIUM |
| BGE-S6 | Make `expected_embedder_id` required in `LocalFAISSStore.load_from_disk()`; all call sites pass `"BAAI/bge-m3"` | MEDIUM |
| BGE-S7 | Add dimension assertion (`assert len(vec) == 1024`) in `LocalFAISSStore.add_vectors()` when embedder is BGE-m3 | MEDIUM |
| BGE-S8 | Add SSOT constants `BGE_MODEL_ID = "BAAI/bge-m3"` and `BGE_EMBEDDING_DIM = 1024` to `structure_blueprint_config.py` | MEDIUM |
| BGE-S9 | Execute top-priority items from `bge-faiss-complete-embedding-plan-cd71f9.md` — O(N) scan replacements in `apps_rg/` and `apps_lic/` | MEDIUM |
| BGE-S10 | Add model checksum verification for `BAAI/bge-m3` weights at first load in `_get_model()` | LOW |

---

## 3. Semantic Cache — Gaps & Plan

### 3.1 Current State (Graph-Confirmed)

- `semantic_cache_manager.py` has **2 `bmg_embed_text` call sites** — BGE is already wired for embedding (contradicts earlier assumption; `SimpleEmbedder` may have been replaced).
- **63 symbol edges** target `semantic_cache` — callers: `test_semantic_cache_activation.py` (34), `_probe_deep_hardening.py` (8), various L1/L4/L5 files.
- `InMemoryVectorStore` still referenced in `semantic_cache_manager.py` — the FAISS migration for long-term store is **not yet complete**.
- `agentic_core/mixins/semantic_cache_mixin.py:44` has a confirmed `L_SHARED->L4` layer violation (governance graph).
- **4 antipatterns** confirmed in `L4_state/memory/` files: 2 in `reasoning_memory.py`, 1 in `sovereign_reasoning_memory_ledger.py`, 1 in `sovereign_semantic_cache.py` — all `silent_exception_swallow`.
- `sovereign_semantic_cache.py` is a **separate file** from `semantic_cache_manager.py` — potential duplication; needs ownership verification.

### 3.2 Identified Gaps (ADG-Verified)

| ID | Gap | ADG Evidence | Location |
|---|---|---|---|
| SC-01 | `InMemoryVectorStore` still referenced in `semantic_cache_manager.py` and `sovereign_semantic_cache.py` — FAISS migration incomplete for long-term store | Symbol graph: 3 files using `InMemoryVectorStore` | `L4_state/memory/` |
| SC-02 | `semantic_cache_mixin.py:44` has `L_SHARED->L4` layer violation — mixin directly imports L4 state instead of using an injected port | Governance graph | `mixins/semantic_cache_mixin.py:44` |
| SC-03 | `sovereign_semantic_cache.py` exists alongside `semantic_cache_manager.py` — potential duplicate canonical implementation; not covered by the hardening evidence | Symbol graph: separate module | `L4_state/memory/sovereign_semantic_cache.py` |
| SC-04 | `reasoning_memory.py` has 2 `silent_exception_swallow` antipatterns (lines 258, 280) | Governance graph | `reasoning_memory.py` |
| SC-05 | `sovereign_reasoning_memory_ledger.py:87` has `silent_exception_swallow` | Governance graph | `sovereign_reasoning_memory_ledger.py:87` |
| SC-06 | `sovereign_semantic_cache.py:149` has bare `except:` swallow | Governance graph | `sovereign_semantic_cache.py:149` |
| SC-07 | No FAISS persist/load across process restarts — `InMemoryVectorStore` is ephemeral; promoted entries are lost on restart | Cross-cutting | `semantic_cache_manager.py` |
| SC-08 | No L6 observability spans emitted from cache hit/miss/store events | Source confirmed | `semantic_cache_manager.py` |
| SC-09 | `semantic_update_feedback()` scores not persisted to L4 for `PolicyRecommendationEngine` | Source confirmed | `semantic_cache_mixin.py` |
| SC-10 | Redis client defaults to disabled — working-memory (L1) cache non-functional by default | Evidence confirmed | `semantic_cache_manager.py` |

### 3.3 Implementation Steps

| Step | Action | Priority |
|---|---|---|
| SC-S1 | Audit `sovereign_semantic_cache.py` vs `semantic_cache_manager.py` — confirm canonical ownership; deprecate duplicate if confirmed | HIGH |
| SC-S2 | Replace `InMemoryVectorStore` in `semantic_cache_manager.py` and `sovereign_semantic_cache.py` with `LocalFAISSStore` (`embedder_id="BAAI/bge-m3"`) | HIGH |
| SC-S3 | Fix `semantic_cache_mixin.py:44` layer violation — inject L4 `SemanticCacheManager` via constructor parameter instead of direct import | HIGH |
| SC-S4 | Add FAISS index persistence: `LocalFAISSStore.persist_to_disk()` on graceful shutdown; `load_from_disk(expected_embedder_id="BAAI/bge-m3")` on startup | HIGH |
| SC-S5 | Fix 4 `silent_exception_swallow` antipatterns in `reasoning_memory.py` (2), `sovereign_reasoning_memory_ledger.py` (1), `sovereign_semantic_cache.py` (1) | MEDIUM |
| SC-S6 | Implement L2 vector store TTL — add `created_utc` metadata to FAISS entries; `cleanup_expired()` calls `LocalFAISSStore.prune()` + `rebuild()` | MEDIUM |
| SC-S7 | Persist `semantic_update_feedback()` scores to L4 state registry; expose for `PolicyRecommendationEngine` consumption | MEDIUM |
| SC-S8 | Emit L6 observability spans for cache hit/miss (L1+L2), Redis state changes, FAISS rebuild, TTL eviction | MEDIUM |
| SC-S9 | Add operator alert event `semantic_cache.redis_unavailable` for monitoring | LOW |

---

## 4. Evaluation Metrics & Criteria — Gaps & Plan

### 4.1 Current State (Graph-Confirmed)

**Sub-packages confirmed to EXIST on disk** (have exports in file graph):
- `agentic_core/evaluation/__init__.py`
- `agentic_core/evaluation/judges/llm_judge.py`
- `agentic_core/evaluation/metrics/__init__.py`, `base.py`, `ragas_metrics.py`
- `agentic_core/evaluation/retrieval/__init__.py`, `l4_registries.py`

**Sub-packages confirmed to NOT EXIST** (dead imports in graphsnap — 67 total):
- `evaluation/__init__.py` → `runners/` and `schemas/` packages (5 dead imports)
- `evaluation/metrics/__init__.py` → 11 dead imports: `answer_correctness`, `completeness_metrics` (6 classes), `groundedness`, `mrr`, `ndcg`, `precision_at_k`, `recall_at_k`, `base` (3 classes)
- `evaluation/retrieval/__init__.py` → 51 dead imports across: `answer_support`, `completeness`, `completeness_reranker`, `completeness_scorer`, `fusion`, `interfaces`, `late_chunking`, `meta_learning_bridge`, `parent_child`, `profiles`, `reranker`

**Test coverage confirmed** (test graph — 36 unique covered symbols):
- Tests reference `evaluation.runners.offline_eval_runner`, `evaluation.schemas.*`, all 7 missing metric modules — but these are tested via `ModuleNotFoundError` guards, not actual implementations.
- **`evaluation.monitoring`** sub-package referenced in tests (`drift_monitor`, `completeness_monitors`, `shadow_eval_runner`, `snapshots`) — NOT in the existing file graph — also missing.
- **`evaluation.chunking`** sub-package referenced — NOT in file graph — also missing.
- **`evaluation.feedback`** sub-package referenced — NOT in file graph — also missing.
- **`evaluation.config.thresholds`** — zero test coverage, does not exist.
- `evaluation.retrieval.meta_learning_bridge.CompletenessRAGProposer` referenced in test graph — the bridge class is listed as dead import in `retrieval/__init__.py`.

**Completely isolated** — 0 non-test, non-evaluation files import from `agentic_core/evaluation` (file graph). Evaluation runs standalone only.

### 4.2 Identified Gaps (ADG-Verified)

| ID | Gap | ADG Evidence | Location |
|---|---|---|---|
| EV-01 | `evaluation/runners/` package missing — 2 dead imports in `evaluation/__init__.py` | Graphsnap: 5 dead imports | `evaluation/__init__.py` |
| EV-02 | `evaluation/schemas/` package missing — 3 dead imports | Graphsnap | `evaluation/__init__.py` |
| EV-03 | 7 metric files missing — 11 dead imports in `evaluation/metrics/__init__.py` | Graphsnap | `evaluation/metrics/` |
| EV-04 | `evaluation/retrieval/` sub-modules missing — **51 dead imports** in `evaluation/retrieval/__init__.py` | Graphsnap: largest dead-import cluster | `evaluation/retrieval/__init__.py` |
| EV-05 | `evaluation/monitoring/` sub-package missing — `drift_monitor`, `completeness_monitors`, `shadow_eval_runner`, `snapshots` all tested but not on disk | Test graph: covered but missing | `evaluation/monitoring/` |
| EV-06 | `evaluation/chunking/` sub-package missing — `policies`, `validators` tested but not on disk | Test graph | `evaluation/chunking/` |
| EV-07 | `evaluation/feedback/` sub-package missing — `dpo_batch_builder`, `proposer_bridge`, `schemas` tested but not on disk | Test graph | `evaluation/feedback/` |
| EV-08 | `evaluation.config.thresholds` does not exist — no formal pass/fail threshold constants | Test graph: zero coverage, source: missing | `evaluation/config/` |
| EV-09 | `evaluation.retrieval.meta_learning_bridge.CompletenessRAGProposer` is dead import — the bridge between evaluation and system_learning is broken | Graphsnap dead import | `evaluation/retrieval/__init__.py` |
| EV-10 | Evaluation is completely isolated — **0 non-test files** import from it | File graph | cross-cutting |
| EV-11 | `evaluation.metrics.completeness_metrics` — **zero test coverage** | Test graph | `evaluation/metrics/` |
| EV-12 | `GeminiJudge` has **L_SHARED->L2** effective dependency via `SovereignLLMGateway` — vendor lock-in + potential layer issue | Symbol graph | `evaluation/judges/llm_judge.py` |
| EV-13 | No CI gate based on evaluation metrics — evaluation suite can degrade with no build failure | `.github/workflows/` | `.github/` |
| EV-14 | No golden evaluation datasets — `evaluation/datasets/` is absent from file graph entirely | File graph | `evaluation/datasets/` |

### 4.3 Formal Metric Definitions & Pass/Fail Criteria

To be codified as frozen constants in `agentic_core/evaluation/config/thresholds.py`:

| Metric | Definition | Minimum Pass | Target |
|---|---|---|---|
| `faithfulness` | Fraction of answer sentences attributable to context (cosine ≥ 0.75) | 0.70 | 0.85 |
| `answer_relevancy` | Cosine similarity between query embedding and answer embedding | 0.65 | 0.80 |
| `context_precision` | `|relevant ∩ retrieved| / |retrieved|` | 0.60 | 0.75 |
| `groundedness` | Fraction of answer claims attributable to context | 0.70 | 0.85 |
| `precision_at_k` | `|relevant ∩ top-k| / k` | 0.50 | 0.70 |
| `recall_at_k` | `|relevant ∩ top-k| / |relevant|` | 0.60 | 0.80 |
| `MRR` | Mean Reciprocal Rank of first relevant result | 0.50 | 0.70 |
| `NDCG@k` | Normalised Discounted Cumulative Gain at k | 0.55 | 0.75 |
| `answer_correctness` | Semantic similarity of answer to ground-truth | 0.70 | 0.85 |
| `missing_condition_rate` (L4G) | Rate of queries missing conditional context | < 0.15 | < 0.05 |
| `high_similarity_wrong_answer_rate` (L4G) | High-cosine retrievals producing wrong answers | < 0.10 | < 0.03 |

### 4.4 Implementation Steps

| Step | Action | Priority |
|---|---|---|
| EV-S1 | Create `evaluation/retrieval/` sub-modules: `answer_support.py`, `completeness.py`, `completeness_reranker.py`, `completeness_scorer.py`, `fusion.py`, `interfaces.py`, `late_chunking.py`, `meta_learning_bridge.py`, `parent_child.py`, `profiles.py`, `reranker.py` (resolves 51 dead imports) | HIGH |
| EV-S2 | Create `evaluation/schemas/` package: `evaluation_dataset_schema.py` (`EvaluationExample`), `evaluation_result_schema.py` (`EvaluationResult`, `EvaluationReport`) | HIGH |
| EV-S3 | Create `evaluation/runners/` package: `offline_eval_runner.py`, `replay_eval_runner.py` | HIGH |
| EV-S4 | Create 7 missing metric files: `precision_at_k.py`, `recall_at_k.py`, `mrr.py`, `ndcg.py`, `groundedness.py`, `answer_correctness.py`, `completeness_metrics.py` | HIGH |
| EV-S5 | Create `evaluation/monitoring/` package: `drift_monitor.py`, `completeness_monitors.py`, `shadow_eval_runner.py`, `snapshots.py` | HIGH |
| EV-S6 | Create `evaluation/feedback/` package: `dpo_batch_builder.py`, `proposer_bridge.py`, `schemas.py` | HIGH |
| EV-S7 | Create `evaluation/chunking/` package: `policies.py`, `validators.py` | HIGH |
| EV-S8 | Create `evaluation/config/thresholds.py` with frozen threshold constants from §4.3 | HIGH |
| EV-S9 | Wire `evaluation.retrieval.meta_learning_bridge.CompletenessRAGProposer` as concrete `RAGProposer` in `meta_learning_pipeline.py` (connects evaluation to system_learning) | MEDIUM |
| EV-S10 | Add `BGEJudge` to `evaluation/judges/` — local judge using `bmg_embed_text()` — eliminates Gemini lock-in | MEDIUM |
| EV-S11 | Persist `EvaluationReport` JSON to `docs/reports/evaluation/` after each `OfflineEvaluationRunner` run | MEDIUM |
| EV-S12 | Add golden dataset under `evaluation/datasets/` — minimum 20 `EvaluationExample` records | MEDIUM |
| EV-S13 | Add CI workflow `evaluation-gate.yml` that fails build if any metric drops below minimum pass threshold | MEDIUM |
| EV-S14 | Add `ContextCompletenessSnapshot` trend analysis — alert if any rate increases > 0.05 vs 5-snapshot rolling mean | LOW |
| EV-S15 | Add test coverage for `completeness_metrics` and `evaluation.config.thresholds` (currently at zero) | LOW |

---

## 5. Global Governance Debt (ADG-Derived)

### 5.1 Antipatterns to Fix (Codebase-Wide)

| Kind | Count | Priority |
|---|---|---|
| `retry_without_backoff` | **804** | HIGH — can cause cascade failures |
| `silent_exception_swallow` | **577** | HIGH — hides real errors |
| `global_state_mutation` | **70** | MEDIUM |
| `blocking_call_in_async` | **8** | MEDIUM |

Target-area specific antipatterns: **35** across 19 files (detailed in §1–§3 above).

### 5.2 Layer Violations to Fix

**Top violation files:**
- `agentic_core/L0_routing/scripts/execute_ssot.py` — **8 violations** (highest in codebase)
- `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` — 5 violations
- `agentic_core/base_agents/SovereignBaseAgent.py` — 4 violations
- `agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py` — 3 violations
- `agentic_core/mixins/hardening_mixin.py` — 3 violations
- `agentic_core/mixins/meta_learning_client_mixin.py` — 3 violations
- `agentic_core/utils/workflow_engines/drift_monitor.py` — 3 violations

### 5.3 SSOT Constants Still Needed

| Constant | Purpose |
|---|---|
| `EMBEDDING_PACK_ROOT` | Replace `C:/AgenticEmbeddings/` hardcode |
| `BGE_MODEL_ID` | Replace `"BAAI/bge-m3"` string literals (48+ sites) |
| `BGE_EMBEDDING_DIM` | Replace `1024` literals |

---

## 6. Sprint Sequencing (ADG-Revised)

### Sprint 1 — Unblock Evaluation (67 dead imports eliminated)
- EV-S1 — create `evaluation/retrieval/` sub-modules (51 dead imports)
- EV-S2 — create `evaluation/schemas/` (3 dead imports)
- EV-S3 — create `evaluation/runners/` (2 dead imports)
- EV-S4 — 7 missing metric files (11 dead imports)
- EV-S5, EV-S6, EV-S7 — `monitoring/`, `feedback/`, `chunking/` packages
- EV-S8 — threshold constants

### Sprint 2 — BGE Exclusivity + Embedding Activation
- BGE-S1 — remove `OpenAIEmbedder` from `openai_embedder.py`
- BGE-S2 — remove non-BGE models from governance allowlists
- BGE-S3 — fix `replay_key()` model ID
- SL-S5 — flip `EMBEDDING_ENABLED` default to `True` via L4
- BGE-S8 — add `BGE_MODEL_ID`, `BGE_EMBEDDING_DIM` SSOT constants

### Sprint 3 — Semantic Cache FAISS Migration
- SC-S1 — audit `sovereign_semantic_cache.py` vs `semantic_cache_manager.py`
- SC-S2 — replace `InMemoryVectorStore` with `LocalFAISSStore`
- SC-S3 — fix `semantic_cache_mixin.py:44` layer violation
- SC-S4 — FAISS persist/load on startup/shutdown

### Sprint 4 — Layer Violations + Antipatterns
- SL-S3 — fix 5 layer violations in target area
- SL-S4 — fix 21 `silent_exception_swallow` in target area
- SC-S5 — fix 4 antipatterns in `L4_state/memory/`
- BGE-S5 — fix 2 antipatterns in `bmg_embedding_similarity.py`
- SL-S7 — fix `execute_ssot.py` L0 layer violation

### Sprint 5 — Learning Loop Closure + CI Gate
- SL-S6 — concrete proposer implementations
- EV-S9 — wire `CompletenessRAGProposer` into `meta_learning_pipeline`
- SC-S7 — persist feedback scores for `PolicyRecommendationEngine`
- EV-S13 — CI evaluation gate
- SL-S8 — wire `evaluation` bridge as `RAGProposer`

---

## 7. Complete File Inventory

### Files to Create (New — 26 total)

| File | Resolves |
|---|---|
| `agentic_core/evaluation/retrieval/answer_support.py` | EV-01 (51 dead imports) |
| `agentic_core/evaluation/retrieval/completeness.py` | EV-01 |
| `agentic_core/evaluation/retrieval/completeness_reranker.py` | EV-01 |
| `agentic_core/evaluation/retrieval/completeness_scorer.py` | EV-01 |
| `agentic_core/evaluation/retrieval/fusion.py` | EV-01 |
| `agentic_core/evaluation/retrieval/interfaces.py` | EV-01 |
| `agentic_core/evaluation/retrieval/late_chunking.py` | EV-01 |
| `agentic_core/evaluation/retrieval/meta_learning_bridge.py` | EV-01, EV-09 |
| `agentic_core/evaluation/retrieval/parent_child.py` | EV-01 |
| `agentic_core/evaluation/retrieval/profiles.py` | EV-01 |
| `agentic_core/evaluation/retrieval/reranker.py` | EV-01 |
| `agentic_core/evaluation/schemas/__init__.py` | EV-02 |
| `agentic_core/evaluation/schemas/evaluation_dataset_schema.py` | EV-02 |
| `agentic_core/evaluation/schemas/evaluation_result_schema.py` | EV-02 |
| `agentic_core/evaluation/runners/__init__.py` | EV-03 |
| `agentic_core/evaluation/runners/offline_eval_runner.py` | EV-03 |
| `agentic_core/evaluation/runners/replay_eval_runner.py` | EV-03 |
| `agentic_core/evaluation/metrics/precision_at_k.py` | EV-04 |
| `agentic_core/evaluation/metrics/recall_at_k.py` | EV-04 |
| `agentic_core/evaluation/metrics/mrr.py` | EV-04 |
| `agentic_core/evaluation/metrics/ndcg.py` | EV-04 |
| `agentic_core/evaluation/metrics/groundedness.py` | EV-04 |
| `agentic_core/evaluation/metrics/answer_correctness.py` | EV-04 |
| `agentic_core/evaluation/metrics/completeness_metrics.py` | EV-04 |
| `agentic_core/evaluation/monitoring/__init__.py` | EV-05 |
| `agentic_core/evaluation/monitoring/drift_monitor.py` | EV-05 |
| `agentic_core/evaluation/monitoring/completeness_monitors.py` | EV-05 |
| `agentic_core/evaluation/monitoring/shadow_eval_runner.py` | EV-05 |
| `agentic_core/evaluation/monitoring/snapshots.py` | EV-05 |
| `agentic_core/evaluation/feedback/__init__.py` | EV-06 |
| `agentic_core/evaluation/feedback/dpo_batch_builder.py` | EV-06 |
| `agentic_core/evaluation/feedback/proposer_bridge.py` | EV-06 |
| `agentic_core/evaluation/feedback/schemas.py` | EV-06 |
| `agentic_core/evaluation/chunking/__init__.py` | EV-07 |
| `agentic_core/evaluation/chunking/policies.py` | EV-07 |
| `agentic_core/evaluation/chunking/validators.py` | EV-07 |
| `agentic_core/evaluation/config/__init__.py` | EV-08 |
| `agentic_core/evaluation/config/thresholds.py` | EV-08 |
| `agentic_core/evaluation/judges/bge_judge.py` | EV-10 |
| `.github/workflows/evaluation-gate.yml` | EV-13 |

### Files to Modify (Existing — 9 total)

| File | Changes | Steps |
|---|---|---|
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | Add `EMBEDDING_PACK_ROOT`, `BGE_MODEL_ID`, `BGE_EMBEDDING_DIM` | SL-S1, BGE-S8 |
| `system_learning/engines/openai_embedder.py` | Remove `OpenAIEmbedder`; rename to `bge_embedder.py` | BGE-S1, SL-S2 |
| `system_learning/constraints/config_surfaces.py` | Remove non-BGE entries from allowlists | BGE-S2 |
| `system_learning/engines/embedding_service_factory.py` | Fix path (SL-S1), fix replay_key model ID (BGE-S3), wire top_k (SL-S10) | SL-S1, BGE-S3, SL-S10 |
| `system_learning/pipelines/meta_learning_pipeline.py` | Fix `L_SL->L_PG` violation; add `evaluation_report_bytes` field; wire `CompletenessRAGProposer` | SL-S3, EV-S9 |
| `system_learning/engines/shadow_drift_analyzer.py` | Fix `L_SL->L6` violation — emit via callback not direct import | SL-S3 |
| `system_learning/engines/stage_barrier_enforcer.py` | Fix `L_SL->L5` violation | SL-S3 |
| `agentic_core/mixins/semantic_cache_mixin.py` | Fix `L_SHARED->L4` violation; inject manager via port | SC-S3 |
| `agentic_core/L4_state/memory/semantic_cache_manager.py` | Replace `InMemoryVectorStore` with `LocalFAISSStore`; add persist/load | SC-S2, SC-S4 |

---

*Plan complete. All gaps derived directly from ADG graph artifacts. NO CODE CHANGES have been made.*

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

