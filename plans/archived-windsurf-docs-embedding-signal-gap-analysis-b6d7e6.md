---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\embedding-signal-gap-analysis-b6d7e6.md'
original_relative_path: 'embedding-signal-gap-analysis-b6d7e6.md'
source_sha256: d8495a3be3354b59d2e3eff1a639db79d9496f203e6be619d43fb4ae15dc8979
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# OpenAI Embedding Signal Gap Analysis & Activation Roadmap

Detailed architectural gap analysis for incorporating OpenAI `text-embedding-3-large` embeddings across the agentic pipeline to increase semantic search signal, with concrete wiring plan per injection point.

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


## Current Architecture State

### What Exists
| Component | File | State |
|---|---|---|
| `OpenAIEmbedder` | `system_learning/engines/openai_embedder.py` | **Direct SDK import** — bypasses factory (known debt) |
| `EmbeddingServiceFactory` | `system_learning/engines/embedding_service_factory.py` | Uses local `.f32` seed packs (BGE model, 1024-dim — not OpenAI) |
| `MetaLearningEmbeddingService` | `system_learning/engines/meta_learning_embedding_service.py` | Delegates to factory + seed packs; no live OpenAI calls |
| `embedding_factory.py` | `agentic_core/embeddings/embedding_factory.py` | Canonical factory — OpenAI provider registered (Phase 10) |
| `RetrievalProfile` | `system_learning/engines/retrieval_profile.py` | `text-embedding-3-small`, top_k=10, cutoff=0.7 — not upgraded |
| `PatternAnalysisEngine` | `system_learning/engines/pattern_analysis_engine.py` | Accepts pre-computed vectors; no live embedder wired |
| `AirlockAssembler` / `GovernedPayload` | `agentic_core/L0_routing/engines/assembly_stage.py` | `c0_context` slot exists but filled by caller; no semantic retrieval |
| `LocalFAISSStore` | `system_learning/engines/local_faiss_store.py` | FAISS index at 1024-dim (BGE); not wired to live OpenAI embeddings |
| `RAGOptimizer` | `system_learning/engines/rag_optimizer.py` | Tunes `retrieval_top_k` on scalar precision only — no semantic signal |

---

## Critical Gaps

### GAP-1: `EmbeddingServiceFactory` uses BGE seed packs, not OpenAI
- Loads local `.f32` files from `C:/AgenticEmbeddings/seed_packs/`
- Manifest hardcodes BGE model metadata (`BAAI/bge-large-en-v1.5`, 1024-dim)
- Live OpenAI query-time embeddings never flow through this factory
- `replay_key()` references `hf_repo` / BGE metadata — stale

### GAP-2: `RetrievalProfile.create_default()` still references `text-embedding-3-small`
- `primary_embedder_id = "text-embedding-3-small"`, `embedding_dim = 1536`
- Not upgraded to `text-embedding-3-large`
- `influence_cap = 0.25` defined but not enforced downstream
- `similarity_cutoff = 0.7` not recalibrated for OpenAI cosine space

### GAP-3: `c0_context` in `GovernedPayload` is not semantically populated
- `AirlockAssembler.assemble()` accepts `c0_context: str` from caller
- No path from embedding retrieval pipeline to this slot
- HS-1 context injection (Phase 10) is a mock — no real plumbing to RAG pipeline

### GAP-4: `PatternAnalysisEngine` has no embedder injection
- Accepts `historical_embeddings: List[List[float]]` — caller must supply pre-computed vectors
- No wiring to `embedding_factory.create_embedding_client("openai")` for new failure signals
- `distance_threshold = 0.5` (Euclidean) was tuned for BGE 1024-dim; invalid for OpenAI 3072-dim space

### GAP-5: Dimension mismatch — BGE 1024-dim seed packs vs OpenAI 3072-dim vectors
- All `.f32` packs are 1024-dim (BGE)
- OpenAI `text-embedding-3-large` produces **3072-dim** vectors (or 1536-dim via Matryoshka)
- Mixing dimensions causes silent shape errors on cosine similarity
- FAISS index also built at 1024-dim

### GAP-6: `MetaLearningEmbeddingService` has no production OpenAI embedder injection
- Constructor takes `embedder: Embedder` — in practice injected as stub or BGE embedder
- No production code path routes `OpenAIEmbedder` through `embedding_factory` into this service

### GAP-7: `RAGOptimizer` uses only scalar `retrieval_precision` — no semantic quality signal
- Heuristic: `if precision < 0.70: increase top_k`
- Mean cosine similarity of retrieved results vs. query is invisible to optimizer
- Cannot distinguish "10 returned but all semantically irrelevant" from "10 high-quality results"

### GAP-8: `openai_embedder.py` imports OpenAI SDK directly — sovereignty violation
- `from openai import OpenAI` — known bypass debt (ceiling=2, should be 0)
- Must route through `embedding_factory.create_embedding_client("openai")`

---

## Proposed Activation Plan (7 Phases)

### Phase A — Model + Dimension Alignment (Foundation)
**Scope**: `system_learning/engines/retrieval_profile.py`, `agentic_core/embeddings/embedding_factory.py`

- Update `RetrievalProfile.create_default()`:
  - `primary_embedder_id = "openai/text-embedding-3-large"`
  - `embedding_dim = 1536` (Matryoshka truncation — halves memory vs 3072, maintains FAISS compat)
  - `similarity_cutoff = 0.75` (recalibrated for OpenAI cosine space)
- Add `dimensions=1536` kwarg to `create_embedding_client("openai")` — passed to `embeddings.create()`
- Update `get_replay_metadata()` to emit correct `k=1536` and model name

---

### Phase B — Live Query Embedder Injection (HS-4 Real Wiring)
**Scope**: `system_learning/engines/meta_learning_embedding_service.py`, `system_learning/engines/seed_embedding_pack_builder.py`

- Replace stub `embedder` in `MetaLearningEmbeddingService.__init__()` with `embedding_factory.create_embedding_client("openai", model="text-embedding-3-large")`
- Add `--provider openai --dimensions 1536` to `seed_pack_build_cli.py` for rebuilding packs at 1536-dim
- Register new pack hash in `EmbeddingServiceFactory._load_pack()` manifest check
- Update `replay_key()` to reference OpenAI model metadata instead of `hf_repo`

---

### Phase C — C0 Semantic Context Population (HS-1 Real Wiring)
**Scope**: New `C0ContextRetriever` in `agentic_core/L0_routing/seams/c0_context_retriever.py`

- `C0ContextRetriever.retrieve(u0_user_prompt: str) -> str`:
  - Embed prompt via `embedding_factory` → retrieve top-k from FAISS seed pack → format as annotated string
  - Output fed into `AirlockAssembler.assemble(c0_context=...)`
  - **Invariant**: Must not modify `s0_system`, `i0_instructional`, or `u0_user_prompt`
  - **Invariant**: C0 is proposal-only — no routing decision side effects
- Add non-mutation assertion at `GovernedPayload` construction (compare manifest hash of system slots before/after)

---

### Phase D — Pattern Clustering with Live Embedder (HS-5 Real Wiring)
**Scope**: `system_learning/engines/pattern_analysis_engine.py`

- Inject `embedder: EmbeddingClient | None = None` into `PatternAnalysisEngine.__init__()`
- Add `analyze_texts(texts: List[str]) -> PatternSummary` — embeds via factory, passes vectors to existing `analyze()`
- Recalibrate `distance_threshold`: cosine distance `0.25` ≈ `1 - 0.75` similarity for OpenAI 1536-dim

---

### Phase E — RLHF/DPO Embedding Audit Context (HS-6 Real Wiring)
**Scope**: `system_learning/engines/rlhf_optimizer.py`, `system_learning/engines/change_package_impl.py`

- Add `embedding_context_hash: str | None = None` to `ChangePackage` as audit-only field
- Not used in threshold computation — governance replay trail only
- Logged by L4 state writer

---

### Phase F — RAG Semantic Quality Signal
**Scope**: `system_learning/engines/rag_optimizer.py`

- Add `mean_cosine_similarity: float` parameter to `propose_rag_param_changes()`
- Tune `top_k` on both precision and semantic floor:
  - `mean_cosine_similarity < 0.65` → increase `top_k` regardless of precision
  - `mean_cosine_similarity > 0.85` AND `precision > 0.85` → decrease `top_k`

---

### Phase G — Sovereignty Closure: Remove Direct SDK Import
**Scope**: `system_learning/engines/openai_embedder.py`

- Remove `from openai import OpenAI`
- Constructor calls `embedding_factory.create_embedding_client("openai", ...)`
- `embed_batch()` delegates to `client.get_embeddings_batch()`
- Clears bypass debt entry; ceiling drops 2 → 1 → 0

---

## Signal Improvement Summary

| Injection Point | Current | Post-Activation |
|---|---|---|
| **HS-1** C0 prompt context | Mock/empty string | Semantic top-k retrieval from seed pack |
| **HS-2** HealingInput enrichment | No embedding signal | Cosine similarity score attached |
| **HS-4** RAG retrieval | BGE 1024-dim seed packs, no live embeddings | OpenAI 1536-dim live query embeddings |
| **HS-5** Pattern clustering | Pre-computed BGE vectors only | Live OpenAI text → embed → cluster pipeline |
| **HS-6** RLHF context | No embedding signal | Embedding context hash in audit trail |
| **RAG optimizer** | Scalar precision only | + mean cosine similarity metric |
| **Sovereignty** | `openai_embedder.py` bypasses factory | Routed through `embedding_factory` |
| **Dimension alignment** | BGE 1024-dim / small 1536-dim mixed | OpenAI `text-embedding-3-large` 1536-dim unified |

---

## Implementation Order (Risk-Sequenced)

| Priority | Phase | Risk | Files |
|---|---|---|---|
| 1 | A — Model + dimension alignment | Low (no runtime change) | 2 |
| 2 | G — Remove bypass debt | Low (refactor only) | 1 |
| 3 | D — Pattern clustering additive method | Low | 1 |
| 4 | F — RAG semantic signal additive metric | Low | 1 |
| 5 | E — RLHF audit context additive field | Low | 2 |
| 6 | B — Live embedder injection | Medium (new API calls at runtime) | 2 |
| 7 | C — C0 semantic context new component | Medium | 2 |

---

## Acceptance Criteria
- `RetrievalProfile.create_default()` emits updated digest referencing `openai/text-embedding-3-large`
- `EmbeddingServiceFactory.replay_key()` references OpenAI model metadata
- No direct `openai` SDK imports outside `embedding_factory.py` (bypass debt ceiling → 0)
- `EMBEDDING_ENABLED=false` → all new paths fail-closed
- `PatternAnalysisEngine.analyze_texts()` produces deterministic output for same text input
- `RAGOptimizer` uses both `retrieval_precision` and `mean_cosine_similarity`
- New governance test: `tests/governance/test_phase11_embedding_wiring.py` covering all 7 phases

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

