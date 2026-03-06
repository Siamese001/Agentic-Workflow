# Agentic RAG

## Overview

The Agentic RAG (Retrieval-Augmented Generation) system is a self-optimizing, sovereign retrieval pipeline that spans L1 (Cognition), L3 (Orchestration), and `system_learning` layers. It provides deterministic query decomposition, semantic memory management, embedding-backed vector search, and performance-adaptive parameter tuning.

---

## Architecture

```
User / Agent Request
        │
        ▼
  query_planner (L1)        ← multi-query decomposition, synthetic passages
        │
        ▼
  SemanticMemory (L1)       ← EmbeddingProvider + VectorIndex
        │
        ▼
  SovereignRagOrchestrator (L3)   ← IRagProvider, self-optimizing
        │                          ← adapts retrieval params from L4 config
        ▼
  rag_optimizer (system_learning) ← performance feedback loop
        │
        ▼
  ShadowDriftAnalyzer             ← cosine drift detection on embeddings
```

---

## L1 Cognition — Query Planning

**File:** `agentic_core/L1_cognition/engines/query_planner.py`

`query_planner` handles all query transformation before retrieval.

| Method | Description |
|---|---|
| `multi_query_generation(query)` | Generates N reformulations of the input query for ensemble retrieval |
| `decompose_query(query)` | Breaks complex queries into atomic sub-queries |
| `decompose_and_expand(query)` | Decompose + HyDE (hypothetical document expansion) |
| `generate_synthetic_passages(query)` | Generates synthetic relevant passages for embedding alignment |
| `_clean_json_response(raw)` | Internal JSON normalization for LLM outputs |

---

## L1 Cognition — Semantic Memory

**File:** `agentic_core/L1_cognition/engines/semantic_manager.py`

### `EmbeddingProvider`

| Method | Description |
|---|---|
| `__init__()` | Initializes the embedding backend |
| `embed(text)` | Returns a dense vector for the input text |

### `VectorIndex`

| Method | Description |
|---|---|
| `__init__()` | Initializes index storage |
| `add(vector, metadata)` | Adds an entry to the index |
| `search(query_vector, top_k)` | Returns top-K nearest entries |

### `SemanticEntry`

Container holding a stored embedding and its associated metadata.

### `SemanticMemory`

The primary semantic store. Wraps `EmbeddingProvider` and `VectorIndex`.

| Method | Description |
|---|---|
| `store(text, metadata)` | Embeds and indexes a document |
| `retrieve(query, top_k)` | Full embedding + search pipeline |
| `search(query_vector, top_k)` | Raw vector search bypass |
| `delete(entry_id)` | Removes an entry |
| `clear()` | Wipes the index |

---

## L1 Cognition — Cognitive Node

**File:** `agentic_core/L1_cognition/engines/CognitiveNode.py`

The `CognitiveNode` integrates perception, reasoning, planning, and action into a single async processing unit.

### Sub-nodes

| Class | Description |
|---|---|
| `PerceptionNode` | Input classification via `process_async`, `_classify_input` |
| `ReasoningNode` | Strategy selection via `reason_async`, `_biased_select`, `_generate_reasoning` |
| `PlanningCoordinator` | Step generation via `plan`, `_generate_steps`, `_adjust_with_patterns` |
| `ActionNode` | Single-method `act` executor |

### `CognitiveNode`

| Method | Description |
|---|---|
| `process_async(input)` | Full async perception → reasoning → plan → act pipeline |
| `_query_semantic_memory(query)` | Internal RAG retrieval call |
| `_compute_mission_reward(result)` | Scalar reward for meta-learning feedback |
| `_async_replay_and_learn(result)` | Submits experience to `MetaLearningAgent` |
| `get_statistics()` | Returns latency and success rate metrics |

`CognitiveResult` dataclass output fields: `output`, `thought_type`, `plan`, `memory_used`, `governance`, `latency_ms`, `success`.

---

## L1 Cognition — Cognitive Engine (Refactored)

**File:** `agentic_core/L1_cognition/engines/cognitive_engine.py`

`CognitiveNodeRefactored` is the production variant with caching and lazy prefetch.

| Method | Description |
|---|---|
| `process(input)` / `process_async(input)` | Sync and async entry points |
| `_make_cache_key(input)` | Deterministic cache key for prompt artifact cache |
| `_is_simple_intent(input)` | Fast-path detection for low-complexity requests |
| `_lazy_memory_prefetch(query)` | Non-blocking background semantic memory fetch |
| `_record_metric(name, value)` | Telemetry emission |
| `get_statistics()` / `clear_cache()` | Observability and cache management |

---

## L1 Cognition — Prompt Artifact Cache

**File:** `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

| Class | Methods | Description |
|---|---|---|
| `CompiledPromptCache` | `get`, `set`, `invalidate` | Caches fully compiled prompts by key |
| `TemplateRenderCache` | `get`, `set`, `invalidate` | Caches rendered template strings |

---

## L3 Orchestration — Sovereign RAG Orchestrator

**File:** `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`

`SovereignRagOrchestrator(SovereignBaseAgent, IRagProvider)` is the L3 self-optimizing RAG entry point. It adapts retrieval parameters based on performance feedback stored in L4 versioned configs.

Constructor accepts optional injected components:
- `retriever` — retrieval backend
- `query_planner` — `query_planner` instance
- `guardrail` — governance guardrail
- `engine` — cognitive engine

L4 config is loaded lazily via `_get_active_configs()` to avoid circular imports. Retrieval anchor types (`AnchoredResult`, `RetrievalAnchor`) are also lazy-loaded from `agentic_core/L4_state/types/retrieval_anchor_types.py`.

---

## L3 Orchestration — Context Curator

**File:** `agentic_core/L3_orchestration/engines/context_curator_engine.py`

`ContextCurator(SovereignBaseAgent)` manages the bounded context window during multi-turn agent execution.

| Method | Description |
|---|---|
| `add_chunk(chunk)` | Adds a context chunk, evicting if budget exceeded |
| `remove_chunk(chunk_id)` | Removes by ID |
| `pin_chunk(chunk_id)` | Marks chunk as eviction-immune |
| `unpin_chunk(chunk_id)` | Removes eviction immunity |
| `update_relevance(chunk_id, score)` | Updates relevance weight |
| `prune_by_relevance(threshold)` | Evicts all chunks below threshold |
| `get_context_window()` | Returns current window contents |
| `get_formatted_context()` | Returns context as LLM-ready string |
| `_calculate_total_tokens()` | Token budget accounting |
| `_make_space(needed)` | Eviction strategy runner |

---

## L3 Orchestration — Redis Orchestrator

**File:** `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py`

`SovereignRedisOrchestrator` — dataclass providing Redis-backed orchestration state persistence. Used for cross-process healing state sharing.

---

## System Learning — RAG Optimizer

**File:** `system_learning/engines/rag_optimizer.py` (scanned in `rag` topic)

Provides performance-driven parameter proposals back to `SovereignRagOrchestrator` via the L4 state store. Connects retrieval metrics (latency, precision, recall) to `L4StateWriter` calls (`write_l4c_retrieval_profile_proposal`).

---

## System Learning — Shadow Drift Analyzer

**File:** `system_learning/engines/shadow_drift_analyzer.py`

Detects embedding distribution drift between control and candidate retrieval outputs.

`ShadowDriftAnalyzer` methods:
- `analyze_batch(pairs)` — processes a batch of `(control_embedding, candidate_embedding)` pairs
- `_compute_percentile(values, pct)` — deterministic percentile
- `_compute_digest(summary)` — SHA-256 digest of drift report

`DriftSummary` dataclass fields:
- `profile_id: str`
- `batch_size: int`
- `mean_cosine: float`
- `p95_cosine: float`
- `drift_flag: bool`
- `drift_score: float`
- `deterministic_digest: str`

`drift_flag` is set when `drift_score` exceeds the configured threshold, triggering a retrieval profile re-proposal.

---

## Retrieval Anchor Types

**File:** `agentic_core/L4_state/types/retrieval_anchor_types.py`

- `RetrievalAnchor` — identifies a specific stored document version pinned for retrieval determinism
- `AnchoredResult` — wraps a retrieval result with its anchor reference for replay verification

---

## RAG Provider Interface

**File:** `agentic_core/L3_orchestration/types/rag_provider_types.py`

| Type | Description |
|---|---|
| `IRagProvider` | Protocol: `retrieve(query: RagQuery) -> RagResult` |
| `RagDocument` | A stored document with content and metadata |
| `RagQuery` | Structured retrieval request |
| `RagResult` | Retrieved documents with relevance scores |

---

## Replay Envelope — RAG Parameters

`ReplayEnvelope` (in `agentic_core/L2_execution/types/replay_envelope_types.py`) captures the full retrieval configuration surface for replay verification:

| Field | Description |
|---|---|
| `embedder_provider: str` | Embedding provider identifier |
| `embedder_model: str` | Embedding model identifier |
| `embedder_dim: int` | Embedding dimension |
| `normalization_policy: str` | L2 / none |
| `chunking_policy: str` | Chunking strategy identifier |
| `distance_metric: str` | cosine / l2 |
| `retrieval_top_k: int` | Top-K parameter |
| `retrieval_similarity_cutoff: float` | Minimum similarity threshold |

Any change to these fields produces a different `replay_key`, making retrieval parameter drift detectable during replay.
