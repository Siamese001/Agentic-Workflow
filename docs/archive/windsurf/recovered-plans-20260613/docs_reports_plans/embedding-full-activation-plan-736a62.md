# OpenAI Embedding Full Activation + Hardening Plan

Complete plan to wire `text-embedding-3-large` into all HS injection points, eliminate bypass debt, enforce structural non-influence on routing, and add privacy/determinism guarantees.

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


## Architecture Snapshot

| Component | File | Current State |
|---|---|---|
| `OpenAIEmbedder` | `system_learning/engines/openai_embedder.py` | Direct `openai` SDK import — sovereignty bypass |
| `EmbeddingServiceFactory` | `system_learning/engines/embedding_service_factory.py` | BGE 1024-dim `.f32` seed packs; replay key uses BGE metadata |
| `MetaLearningEmbeddingService` | `system_learning/engines/meta_learning_embedding_service.py` | Stub/BGE embedder injected; no live OpenAI calls |
| `embedding_factory.py` | `agentic_core/embeddings/embedding_factory.py` | Canonical factory — OpenAI provider registered (Phase 10) |
| `RetrievalProfile` | `system_learning/engines/retrieval_profile.py` | `text-embedding-3-small`, dim=1536, cutoff=0.7 — stale |
| `PatternAnalysisEngine` | `system_learning/engines/pattern_analysis_engine.py` | Accepts pre-computed vectors; Euclidean 0.5 threshold (BGE-tuned) |
| `AirlockAssembler` / `GovernedPayload` | `agentic_core/L0_routing/engines/assembly_stage.py` | `c0_context` slot filled by caller; no semantic retrieval |
| `LocalFAISSStore` | `system_learning/engines/local_faiss_store.py` | FAISS at 1024-dim (BGE); not wired to OpenAI |
| `RAGOptimizer` | `system_learning/engines/rag_optimizer.py` | Tunes `top_k` on scalar precision only |
| `HardeningMixin` | `agentic_core/mixins/hardening_mixin.py:187` | `import tiktoken` directly — known bypass debt entry |
| `DeterministicReplayEngine` | `system_learning/engines/deterministic_replay_engine.py` | Synthetic cases use 8-dim toy vectors vs 1536-dim production |

---

## Gap Register (15 Gaps)

### Activation Gaps

**GAP-1: `EmbeddingServiceFactory` uses BGE seed packs, not OpenAI**
- Factory loads `.f32` files from `C:/AgenticEmbeddings/seed_packs/` at 1024-dim
- Manifest hardcodes `BAAI/bge-large-en-v1.5` — `replay_key()` references BGE `hf_repo`
- Live OpenAI query-time embeddings never flow through this factory

**GAP-2: `RetrievalProfile` not upgraded to `text-embedding-3-large`**
- `primary_embedder_id = "text-embedding-3-small"`, `embedding_dim = 1536`
- `similarity_cutoff = 0.7` not recalibrated for OpenAI cosine space
- `influence_cap = 0.25` defined but not enforced anywhere downstream

**GAP-3: `c0_context` slot in `GovernedPayload` is not semantically populated**
- `AirlockAssembler.assemble()` takes `c0_context: str` from caller
- HS-1 injection (Phase 10) is a mock — no real plumbing to RAG pipeline

**GAP-4: `PatternAnalysisEngine` has no embedder injection**
- Accepts pre-computed `List[List[float]]` — caller must supply vectors
- `distance_threshold = 0.5` Euclidean tuned for BGE 1024-dim; invalid for OpenAI 3072-dim

**GAP-5: Dimension mismatch — BGE 1024-dim vs OpenAI 3072/1536-dim**
- All `.f32` packs are 1024-dim; FAISS index also 1024-dim
- Mixing with OpenAI 3072-dim causes silent shape errors on cosine similarity
- Matryoshka 1536-dim is the resolution: halves memory, maintains FAISS compat

**GAP-6: `MetaLearningEmbeddingService` has no production OpenAI embedder injection**
- Constructor takes `embedder: Embedder` — receives stub or BGE at runtime
- No code path routes `OpenAIEmbedder` through `embedding_factory` into this service

**GAP-7: `RAGOptimizer` uses only scalar `retrieval_precision` — no semantic signal**
- `if precision < 0.70: increase top_k` — blind to semantic quality of results
- Mean cosine similarity of returned candidates vs. query is invisible

### Hardening Gaps

**GAP-8: `tiktoken` import in `hardening_mixin.py` is permanent bypass debt**
- `import tiktoken` at line 187 (token counting for LLM prompt budgets, not embedding)
- Listed as `KNOWN_EMBEDDING_BYPASS_DEBT` — no expiry, becomes permanent bypass lane
- Scanner ceiling is 2; needs to reach 0

**GAP-9: AST scanner detects but does not block**
- `test_no_new_embedding_bypass_violations`: `assert found <= ceiling` — soft check
- No rule for `faiss` direct imports outside `local_faiss_store.py`
- No rule for `openai.embeddings` call-sites (only import detection)
- Allowlist entries are string paths — not cryptographically bound to file content

**GAP-10: Replay key does not include embedder identity**
- `get_replay_metadata()` returns `version: "1.0"` (static, not response-observed)
- Missing: `normalization_policy`, `chunking_policy`, `observed_dim`
- `DeterministicReplayEngine` synthetic cases use 8-dim toy vectors — shape-inconsistent with 1536-dim production

**GAP-11: No structural enforcement of embedding output non-influence on routing**
- Phase 10 tests *assert* non-mutation but nothing in the type system prevents it
- `GovernedPayload.manifest_hash` includes `c0_context` — embedding output participates in routing hash
- No `sealed decision record` pattern: routing decisions could be computed after `c0_context` is set

**GAP-12: Kill-switch only checked at factory init, not at each HS seam**
- `EmbeddingServiceFactory.get_or_disabled()` checks kill-switch once
- Individual HS injection points do not re-check; no audit signal when disabled
- No explicit log line emitted per seam when `EMBEDDING_ENABLED=false`

**GAP-13: No deterministic cache key for embedding results**
- `MetaLearningEmbeddingService` re-embeds same query on every call
- No canonical text normalization before hashing for cache key
- Platform BLAS behavior can affect cosine similarity in `PatternAnalysisEngine` (Euclidean, not cosine)

**GAP-14: No privacy boundary at embedding seam**
- No field allowlist specifying which text fields are allowed to be embedded
- No redaction of API keys / secrets before `embed_batch()` call
- Logging may emit raw embedded text instead of hash+size only

**GAP-15: `openai_embedder.py` is a sovereignty bypass that must be retired**
- `from openai import OpenAI` direct SDK instantiation
- Parallel to `embedding_factory` rather than delegating to it
- Retirement blocked by GAP-6 (factory not yet injected into `MetaLearningEmbeddingService`)

---

## Implementation Plan (10 Phases)

### Phase A — Model + Dimension Alignment *(foundation for all others)*
**Files:** `system_learning/engines/retrieval_profile.py`, `agentic_core/embeddings/embedding_factory.py`

- `RetrievalProfile.create_default()`:
  - `primary_embedder_id = "openai/text-embedding-3-large"`
  - `embedding_dim = 1536` (Matryoshka truncation)
  - `similarity_cutoff = 0.75`
  - Add `normalization_policy: str = "l2"` to `to_canonical_json()` so profile digest reflects it
- `embedding_factory.py` → `create_embedding_client("openai")`:
  - Pass `dimensions=1536` to `embeddings.create()`
  - `get_replay_metadata()` adds `normalization_policy`, `chunking_policy`, `observed_dim` (populated on first call)

*Closes: GAP-2, GAP-10 (partial)*

---

### Phase B — `TokenCountAdapter` + Zero Bypass Debt
**Files:** new `agentic_core/embeddings/token_count_adapter.py`, `agentic_core/mixins/hardening_mixin.py`

- Create `TokenCountAdapter` wrapping `tiktoken` — single import point, on AST scanner allowlist
- `hardening_mixin.py:187` calls `TokenCountAdapter.count_tokens()` — removes direct `tiktoken` import
- Update `KNOWN_EMBEDDING_BYPASS_DEBT` → empty set; `KNOWN_EMBEDDING_BYPASS_DEBT_CEILING = 0`

*Closes: GAP-8*

---

### Phase C — AST Scanner Zero-Tolerance + Cryptographic Allowlist
**File:** `tests/governance/test_phase10_embedding_non_mutation.py`

- Replace `assert found <= ceiling` with `assert found == 0`
- Extend `FORBIDDEN_EMBEDDING_IMPORTS` to include `faiss` (allowed only in `local_faiss_store.py`)
- Add call-site scan: detect `openai.embeddings.*` and `openai.Embedding.*` outside factory
- Allowlist format: `{"path": "agentic_core/embeddings/embedding_factory.py", "sha256": "<sha256_of_file>"}` — file content change breaks CI
- Print: `EMBEDDING-BYPASS-DEBT: found=0, ceiling=0, delta=0` ✓

*Closes: GAP-9*

---

### Phase D — Replay Key + Deterministic Replay Engine Fix
**Files:** `agentic_core/embeddings/embedding_factory.py`, `system_learning/engines/deterministic_replay_engine.py`, `system_learning/engines/embedding_service_factory.py`

- `get_replay_metadata()` exposes: `provider`, `model`, `observed_dim`, `normalization_policy`, `chunking_policy`
- `EmbeddingServiceFactory.replay_key()` references `provider=openai`, `model=text-embedding-3-large`, `dim=1536` instead of BGE metadata
- `DeterministicReplayEngine` synthetic cases: reshape vectors to `RetrievalProfile.embedding_dim` (1536-dim unit vectors)

*Closes: GAP-10*

---

### Phase E — Kill-Switch at Every HS Seam + Audit Signal
**Files:** `agentic_core/embeddings/embedding_factory.py`, each HS injection site

- Add `EmbeddingFactory.is_enabled() -> bool` class method
- Each HS injection point:
  ```python
  if not EmbeddingFactory.is_enabled():
      logger.warning("EMBEDDING_DISABLED: site=%s component=%s", hs_id, cls.__name__)
      return <neutral_value>
  ```
- No silent heuristic fallback — return `None` / empty only
- Exactly one structured log line per seam when disabled

*Closes: GAP-12*

---

### Phase F — Deterministic Cache Key + Stable Float Contract
**Files:** `agentic_core/embeddings/embedding_factory.py`, `system_learning/engines/pattern_analysis_engine.py`

- **Cache key**: `SHA-256(canonical_utf8(text) + "|" + provider + "|" + model + "|" + str(dimensions))`
  - In-process only; no disk persistence
- **`PatternAnalysisEngine`**:
  - Switch from Euclidean to cosine distance: `1 - cosine_similarity` (platform-independent on normalized vectors)
  - New threshold: `0.25` (= 1 − 0.75 similarity) for OpenAI 1536-dim space
  - Add eps-guard normalization before clustering
  - Add `analyze_texts(texts: List[str]) -> PatternSummary` — embeds via factory then calls existing `analyze()`

*Closes: GAP-4 (partial), GAP-13*

---

### Phase G — Privacy Boundary: `EmbeddingInputGuard`
**Files:** new `agentic_core/embeddings/embedding_input_guard.py`

- **Field allowlist**: only `u0_user_prompt`, `failure_signal.error_message`, `pattern_text`, `rag_query` may be embedded
- **Redaction**: strip `sk-...` / `Bearer ...` / sovereign config secret patterns before `embed_batch()`
- **Logging contract**: `logger.info("Embedding: hash=%s size=%d model=%s", sha256[:16], len(text), model)` — never raw text
- AST scanner rule: detect `logger.*` calls with embedding variable names containing raw text

*Closes: GAP-14*

---

### Phase H — Structural Non-Influence: `EmbeddingArtifact` + Routing Hash Split
**Files:** `system_learning/types/embedding_artifact.py`, `agentic_core/L0_routing/engines/assembly_stage.py`

- `EmbeddingArtifact`: add `influence_class: Literal["C0_INFORMATIONAL"] = "C0_INFORMATIONAL"`; add `assert_non_authoritative()` raising if used in non-C0 slot
- `GovernedPayload`: add separate `routing_hash` field computed from `s0_system + i0_instructional + u0_user_prompt` only (excluding `c0_context`)
  - `manifest_hash` remains full-payload hash for audit
  - Routing decisions keyed on `routing_hash` — embedding cannot affect them even if `c0_context` changes
- `AirlockAssembler.assemble()`: add `c0_context_source: Literal["static", "embedding_artifact"] = "static"` — when `"embedding_artifact"`, assert `influence_class == "C0_INFORMATIONAL"`

*Closes: GAP-11*

---

### Phase I — Live Query Embedder Injection + Seed Pack Rebuild *(HS-4 real wiring)*
**Files:** `system_learning/engines/meta_learning_embedding_service.py`, `system_learning/engines/seed_embedding_pack_builder.py`, `system_learning/engines/embedding_service_factory.py`

- `MetaLearningEmbeddingService.__init__()`: replace stub with `embedding_factory.create_embedding_client("openai", model="text-embedding-3-large")`
- `seed_pack_build_cli.py`: add `--provider openai --dimensions 1536` flag
- `EmbeddingServiceFactory._load_pack()`: accept new 1536-dim manifest; update pack hash registration
- `EmbeddingServiceFactory.replay_key()`: references OpenAI metadata (Phase D already done)

*Closes: GAP-1, GAP-5, GAP-6*

---

### Phase J — Retire `openai_embedder.py` + C0 Semantic Context + RAG Signal
**Files:** `system_learning/engines/openai_embedder.py`, new `agentic_core/L0_routing/seams/c0_context_retriever.py`, `system_learning/engines/rag_optimizer.py`, `system_learning/engines/rlhf_optimizer.py`

- **`openai_embedder.py`**: remove `from openai import OpenAI`; delegate to `embedding_factory.create_embedding_client("openai")`; `embed_batch()` calls `client.get_embeddings_batch()`. Bypass debt ceiling → 0.
- **`C0ContextRetriever`**: `retrieve(u0_user_prompt) -> str` — embed → FAISS top-k → format annotated string → fed into `AirlockAssembler.assemble(c0_context=..., c0_context_source="embedding_artifact")`
- **`RAGOptimizer`**: add `mean_cosine_similarity: float` parameter; tune `top_k` on both precision and semantic floor (`< 0.65` → increase; `> 0.85` + `precision > 0.85` → decrease)
- **`rlhf_optimizer.py` / `change_package_impl.py`**: add `embedding_context_hash: str | None = None` to `ChangePackage` — audit trail only, not used in threshold computation

*Closes: GAP-3, GAP-7, GAP-15*

---

## Sequenced Execution (Risk Order)

| # | Phase | Gaps Closed | Risk | Files |
|---|---|---|---|---|
| 1 | A — Model alignment | GAP-2, GAP-10p | Low | 2 |
| 2 | B — TokenCountAdapter | GAP-8 | Low | 2 |
| 3 | C — Scanner zero-tolerance | GAP-9 | Low | 1 |
| 4 | D — Replay key fix | GAP-10 | Low | 3 |
| 5 | E — Kill-switch at seams | GAP-12 | Low | 2 |
| 6 | F — Cache key + cosine distance | GAP-4p, GAP-13 | Low | 2 |
| 7 | G — `EmbeddingInputGuard` | GAP-14 | Medium | 1 |
| 8 | H — Routing hash split | GAP-11 | Medium | 2 |
| 9 | I — Live embedder injection | GAP-1, GAP-5, GAP-6 | Medium | 3 |
| 10 | J — Retire bypass + C0 wiring | GAP-3, GAP-7, GAP-15 | Medium | 4 |

---

## Acceptance Criteria

- `EMBEDDING-BYPASS-DEBT: found=0, ceiling=0` — scanner hard-zero
- `RetrievalProfile.profile_digest` updated (reflects `openai/text-embedding-3-large`)
- `EmbeddingServiceFactory.replay_key()` includes `provider=openai`, `model`, `observed_dim`
- `GovernedPayload.routing_hash` excludes `c0_context`; `manifest_hash` includes it
- `EMBEDDING_DISABLED: site=<hs_id>` log line emitted per seam when kill-switch off
- Cache key deterministic: identical text+model → identical key across runs and platforms
- `EmbeddingInputGuard.guard()` strips secrets; logger never contains raw embedded text (AST-verified)
- No direct `openai` SDK imports outside `embedding_factory.py` (AST: cryptographic allowlist)
- All Phase 10 tests pass (12 passed, 1 skipped); new governance test covers all 10 phases

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

