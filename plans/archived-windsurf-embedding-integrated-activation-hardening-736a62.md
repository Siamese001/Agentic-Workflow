---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\embedding-integrated-activation-hardening-736a62.md'
original_relative_path: 'embedding-integrated-activation-hardening-736a62.md'
source_sha256: 6f41224152430fa27c86c7386e4c79f8ab550fae7ffb1addbcf2aec9cb6a2ccc
recovered_status: LOST_RECOVERED
last_commit: 'afefe5d59e4'
last_commit_date: '2026-03-09 13:06:46 -0400'
created_date: '2026-02-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# OpenAI Embedding Integrated Activation + Hardening Plan (Hardened)

Complete integrated plan to wire `text-embedding-3-large` into all HS injection points while simultaneously eliminating bypass debt, enforcing structural non-influence, and adding privacy/determinism guarantees with 10 critical hardening adjustments.

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
| `HardeningMixin` | `agentic_core/mixins/hardening_mixin.py:187` | `import tiktoken` directly — known bypass debt entry |
| `DeterministicReplayEngine` | `system_learning/engines/deterministic_replay_engine.py` | Synthetic cases use 8-dim toy vectors vs 1536-dim production |

---

## Gap Register (15 Gaps → 10 Integrated Phases)

### Activation Gaps (7)

**GAP-1: `EmbeddingServiceFactory` uses BGE seed packs, not OpenAI**
- Factory loads `.f32` files at 1024-dim; manifest hardcodes `BAAI/bge-large-en-v1.5`
- Live OpenAI query-time embeddings never flow through this factory

**GAP-2: `RetrievalProfile` not upgraded to `text-embedding-3-large`**
- `primary_embedder_id = "text-embedding-3-small"`, `similarity_cutoff = 0.7` not recalibrated

**GAP-3: `c0_context` slot in `GovernedPayload` is not semantically populated**
- HS-1 injection (Phase 10) is a mock — no real plumbing to RAG pipeline

**GAP-4: `PatternAnalysisEngine` has no embedder injection**
- Accepts pre-computed vectors; Euclidean threshold tuned for BGE 1024-dim

**GAP-5: Dimension mismatch — BGE 1024-dim vs OpenAI 3072/1536-dim**
- Mixing dimensions causes silent shape errors on cosine similarity

**GAP-6: `MetaLearningEmbeddingService` has no production OpenAI embedder injection**
- Constructor takes stub embedder; no code path routes through `embedding_factory`

**GAP-7: `RAGOptimizer` uses only scalar `retrieval_precision` — no semantic signal**
- Blind to semantic quality of returned candidates

### Hardening Gaps (8)

**GAP-8: `tiktoken` import in `hardening_mixin.py` is permanent bypass debt**
- Listed as `KNOWN_EMBEDDING_BYPASS_DEBT` — no expiry, becomes permanent bypass lane

**GAP-9: AST scanner detects but does not block**
- `assert found <= ceiling` — soft check; no crypto-bound allowlist

**GAP-10: Replay key does not include embedder identity**
- Missing: `normalization_policy`, `chunking_policy`, `observed_dim`, `distance_metric`

**GAP-11: No structural enforcement of embedding output non-influence on routing**
- `c0_context` participates in routing hash — no sealed decision record

**GAP-12: Kill-switch only checked at factory init, not at each HS seam**
- No per-seam check; no audit signal when disabled

**GAP-13: No deterministic cache key for embedding results**
- No canonical text normalization; platform BLAS can affect similarity

**GAP-14: No privacy boundary at embedding seam**
- No field allowlist, no redaction, raw text may appear in logs

**GAP-15: `openai_embedder.py` is a sovereignty bypass that must be retired**
- Direct `openai` SDK instantiation; parallel to factory rather than delegating

---

## Integrated Implementation Plan (10 Phases - Reordered & Hardened)

### Phase 1 — Model Alignment + Zero Bypass Debt (Foundation)
**Files:** `system_learning/engines/retrieval_profile.py`, new `agentic_core/embeddings/tokenization_adapter.py`, `agentic_core/mixins/hardening_mixin.py`, `tests/governance/test_phase10_embedding_non_mutation.py`

**Activation:**
- `RetrievalProfile.create_default()`:
  - `primary_embedder_id = "openai/text-embedding-3-large"`
  - `embedding_dim = 1536` (Matryoshka truncation)
  - `similarity_cutoff = 0.75`
  - Add `normalization_policy: str = "l2"` to digest

**Hardening:**
- Create `TokenCountAdapter` wrapping `tiktoken` — single import point on AST allowlist
- `hardening_mixin.py` calls `TokenCountAdapter.count_tokens()` — removes direct `tiktoken` import
- Update scanner: `KNOWN_EMBEDDING_BYPASS_DEBT = {}`, `KNOWN_EMBEDDING_BYPASS_DEBT_CEILING = 0`
- Replace `assert found <= ceiling` with `assert found == 0` (hard zero)
- **ADJUSTMENT 6:** Extended AST rules:
  - Block call-sites: `.embeddings.create(`, `.Embedding.create(`, `.get_embeddings(`, `.embed(`
  - Block stealth HTTP: `requests.post("https://api.openai.com/...")`, `httpx.post("https://api.openai.com/...")`

*Closes: GAP-2, GAP-8, GAP-9*

---

### Phase 2 — Embedder Identity in Replay Key + Deterministic Replay
**Files:** `agentic_core/embeddings/embedding_factory.py`, `system_learning/engines/embedding_service_factory.py`, `system_learning/engines/deterministic_replay_engine.py`

**Extended Replay Key Material (ADJUSTMENT 4):**
- `provider: "openai"`
- `model: "text-embedding-3-large"`
- `embedding_dimension: 1536` (observed from first API response)
- `tokenization_policy_version: "cl100k_base_v1"`
- `normalization_policy: "l2"`
- `chunking_policy: "none"`
- `distance_metric: "cosine"` ← **NEW**

**Replay Engine Fix (ADJUSTMENT 8):**
- Generate synthetic vectors using `np.zeros(dim)` or deterministic unit vectors
- Do NOT reshape 8-dim → 1536-dim (avoid ambiguous replay semantics)

*Closes: GAP-10*

---

### Phase 3 — Kill-Switch at Every HS Seam + Audit Signal
**Files:** `agentic_core/embeddings/embedding_factory.py`, each HS injection site

**Implementation:**
- Add `EmbeddingFactory.is_enabled()` class method
- Each HS injection point:
  ```python
  if not EmbeddingFactory.is_enabled():
      logger.warning("EMBEDDING_DISABLED: site=%s component=%s", hs_id, cls.__name__)
      return <neutral_value>
  ```
- No silent heuristic fallback — return `None` / empty only

**ADJUSTMENT 10:** Audit log deterministic format:
- No timestamps, no random IDs
- One message per seam, not per call
- Format: `EMBEDDING_DISABLED: site=<hs_id> component=<class>`

*Closes: GAP-12*

---

### Phase 4 — Deterministic Cache Key + Stable Float Contract
**Files:** `agentic_core/embeddings/embedding_factory.py`, `system_learning/engines/pattern_analysis_engine.py`

**Cache Key Formula (ADJUSTMENT 5):**
```
SHA-256(
    normalized_text_bytes + "|" +
    provider + "|" +
    model + "|" +
    str(dimensions) + "|" +
    tokenization_policy_version + "|" +
    normalization_policy + "|" +
    chunking_policy
)
```

**Canonical Text Normalization:**
- Strip BOM, normalize newlines to `\n`, enforce UTF-8
- Explicit `query_vector.astype(np.float32)` before similarity
- `PatternAnalysisEngine`: switch from Euclidean to cosine distance; threshold `0.25` (1 - 0.75 similarity)

*Closes: GAP-4 (partial), GAP-13*

---

### Phase 5 — Privacy Boundary: `EmbeddingInputGuard` (Structural)
**Files:** new `agentic_core/embeddings/embedding_input_guard.py`

**Controls:**
- Field allowlist: only `u0_user_prompt`, `failure_signal.error_message`, `pattern_text`, `rag_query`
- Redaction: strip `sk-...` / `Bearer ...` / sovereign config secrets before `embed_batch()`

**ADJUSTMENT 7:** Structural logging guard:
- `EmbeddingInputGuard` returns dataclass wrapper:
  ```python
  @dataclass(frozen=True)
  class GuardedText:
      redacted_text: str
      hash: str
      size: int
  ```
- Factory only accepts `GuardedText` type (prevents accidental raw string logging)
- AST scanner rule: detect `logger.*` calls with embedding variables containing raw text

**Negative Control:**
```python
def test_w10_data_leak_tamper_xfail():
    os.environ["W10_DATA_LEAK_TAMPER"] = "1"
    with pytest.raises(EmbeddingInputViolation):
        guard_and_embed("sk-12345secret")  # Should be redacted
```

*Closes: GAP-14*

---

### Phase 6 — FAISS Dimension Migration Guard
**Files:** `system_learning/engines/embedding_service_factory.py`, `system_learning/engines/local_faiss_store.py`

**ADJUSTMENT 3:** Dimension migration hardening:
- `manifest.embedding_dim` must equal `RetrievalProfile.embedding_dim`
- `_load_pack()` asserts dimension equality with hard fail on mismatch
- No silent rebuild; explicit error: `FAISS dimension mismatch: manifest=1024, profile=1536`
- This prevents mixed-dimension packs during migration

*Closes: GAP-5 (partial)*

---

### Phase 7 — Live Query Embedder Injection + Seed Pack Rebuild (HS-4)
**Files:** `system_learning/engines/meta_learning_embedding_service.py`, `system_learning/engines/seed_embedding_pack_builder.py`, `system_learning/engines/embedding_service_factory.py`

**Implementation:**
- `MetaLearningEmbeddingService.__init__()`: replace stub with `embedding_factory.create_embedding_client("openai", model="text-embedding-3-large")`
- `seed_pack_build_cli.py`: add `--provider openai --dimensions 1536` flag
- `EmbeddingServiceFactory._load_pack()`: accept new 1536-dim manifest; update pack hash registration

*Closes: GAP-1, GAP-6*

---

### Phase 8 — Structural Non-Mutation Guard (Routing Hash Split) ⚠️ **MOVED BEFORE LIVE EMBEDDINGS**
**Files:** `system_learning/types/embedding_artifact.py`, `agentic_core/L0_routing/engines/assembly_stage.py`, `tests/governance/test_phase10_embedding_non_mutation.py`

**Structural Changes:**
- `EmbeddingArtifact`: add `influence_class: Literal["C0_INFORMATIONAL"] = "C0_INFORMATIONAL"`
- `GovernedPayload`: add separate `routing_hash` computed from `s0_system + i0_instructional + u0_user_prompt` only (excluding `c0_context`)
- `AirlockAssembler.assemble()`: add `c0_context_source` parameter; assert `influence_class == "C0_INFORMATIONAL"` when source is `"embedding_artifact"`

**ADJUSTMENT 2:** Additional routing hash guard:
```python
assert routing_hash == recompute_routing_hash_without_c0()
```
- Governance test: Change embedding vector → `routing_hash` unchanged, `manifest_hash` changed

**New AST Rules:**
- Router modules (`agentic_core/L0_routing/**`) cannot import embedding modules
- Tier router cannot read embedding fields
- Safety policy cannot read embedding context

*Closes: GAP-11*

---

### Phase 9 — C0 Semantic Context Retrieval (HS-1)
**Files:** new `agentic_core/L0_routing/seams/c0_context_retriever.py`, `agentic_core/L0_routing/engines/assembly_stage.py`

**Implementation:**
- `C0ContextRetriever.retrieve(u0_user_prompt) -> GuardedText`:
  - Embed prompt via factory → retrieve top-k from FAISS seed pack → format annotated string
  - Returns `EmbeddingArtifact` with `influence_class="C0_INFORMATIONAL"`
- `AirlockAssembler.assemble()` receives `c0_context` from retriever with `c0_context_source="embedding_artifact"`

*Closes: GAP-3*

---

### Phase 10 — RAG Semantic Quality Signal + RLHF Audit Context + Pattern Clustering + Retire Bypass
**Files:** `system_learning/engines/rag_optimizer.py`, `system_learning/engines/rlhf_optimizer.py`, `system_learning/engines/change_package_impl.py`, `system_learning/engines/pattern_analysis_engine.py`, `system_learning/engines/openai_embedder.py`

**Implementation:**
- `RAGOptimizer`: add `mean_cosine_similarity: float` parameter; tune `top_k` on both precision and semantic floor
- `ChangePackage`: add `embedding_context_hash: str | None = None` (audit trail only)
- `RLHFOptimizer`: attach embedding context hash to DPO proposals
- `PatternAnalysisEngine`: add `analyze_texts(texts: List[str]) -> PatternSummary` — embeds via factory then calls existing `analyze()`
- `openai_embedder.py`: remove `from openai import OpenAI`; delegate to `embedding_factory.create_embedding_client("openai")`

**ADJUSTMENT 9:** RAG optimizer non-mutation invariant:
```
RAGOptimizer adjustments cannot influence:
- ExecutionMode
- Tier escalation
- Safety thresholds
```
Governance test asserts this invariant.

*Closes: GAP-4 (complete), GAP-7, GAP-15*

---

## Critical Hardening Adjustments Applied

| # | Adjustment | Applied In | Why Critical |
|---|---|---|---|
| 1 | **Phase order**: Routing hash split before live embeddings | Phase 8 moved before 7 | Prevents routing contamination |
| 2 | **Routing hash invariant**: `assert routing_hash == recompute_routing_hash_without_c0()` | Phase 8 | Guarantees C0 cannot affect routing |
| 3 | **FAISS dimension guard**: Hard fail on dimension mismatch | Phase 6 | Prevents silent mixed-dimension packs |
| 4 | **Replay key completeness**: Added `distance_metric` | Phase 2 | Replay key changes with metric switch |
| 5 | **Cache key variables**: Added `normalization_policy`, `chunking_policy` | Phase 4 | Cache key invalid after config shift |
| 6 | **AST scanner strengthen**: Call-site + stealth HTTP detection | Phase 1 | Closes indirect bypass routes |
| 7 | **Privacy boundary structural**: `GuardedText` dataclass wrapper | Phase 5 | Prevents accidental raw logging |
| 8 | **ReplayEngine shape lock**: Generate 1536-dim vectors, don't reshape | Phase 2 | Avoids ambiguous replay semantics |
| 9 | **RAG optimizer non-mutation**: Cannot affect routing/tier/safety | Phase 10 | Maintains decision isolation |
| 10 | **Kill-switch audit deterministic**: No timestamps, one per seam | Phase 3 | Prevents digest drift |

---

## Sequenced Execution (Risk-Ordered & Adjusted)

| # | Phase | Gaps Closed | Risk | Files |
|---|---|---|---|---|
| 1 | Model alignment + zero debt | GAP-2, GAP-8, GAP-9 | Low | 4 |
| 2 | Replay key + deterministic replay | GAP-10 | Low | 3 |
| 3 | Kill-switch at seams | GAP-12 | Low | 2 |
| 4 | Cache key + stable floats | GAP-4p, GAP-13 | Low | 2 |
| 5 | Privacy boundary controls | GAP-14 | Medium | 1 |
| 6 | FAISS dimension guard | GAP-5p | Medium | 2 |
| 7 | Live embedder injection | GAP-1, GAP-6 | Medium | 3 |
| 8 | **Structural non-mutation guard** | GAP-11 | **High** | 3 |
| 9 | C0 semantic context | GAP-3 | Medium | 2 |
| 10 | RAG signal + retire bypass | GAP-4, GAP-7, GAP-15 | Medium | 5 |

---

## Acceptance Criteria

**Activation:**
- `RetrievalProfile.profile_digest` updated (reflects `openai/text-embedding-3-large`)
- All HS injection points (HS-1..HS-6) produce live OpenAI embeddings
- `c0_context` populated with semantic retrieval from FAISS seed pack
- `RAGOptimizer` uses both `retrieval_precision` and `mean_cosine_similarity`
- `PatternAnalysisEngine.analyze_texts()` produces deterministic output for same text input

**Hardening:**
- `EMBEDDING-BYPASS-DEBT: found=0, ceiling=0, delta=0` — hard zero
- AST scanner passes with `assert found == 0` (no soft ceiling)
- Router/tier/safety modules have no embedding imports (AST-verified)
- `GovernedPayload.routing_hash` excludes `c0_context`; embedding cannot affect routing decisions
- **Invariant:** `assert routing_hash == recompute_routing_hash_without_c0()` passes
- `EmbeddingFactory.replay_key()` includes all 7 identity fields (including `distance_metric`)
- Cache key identical across platforms for same normalized text
- `EMBEDDING_DISABLED` blocks all HS seams with deterministic audit log
- `EmbeddingInputGuard` returns `GuardedText` wrapper; logger never contains raw text (AST-verified)
- `W10_DATA_LEAK_TAMPER=1` XFAILs on forbidden field
- No direct `openai` SDK imports or stealth HTTP calls outside `embedding_factory.py`
- FAISS dimension mismatch hard-fails with explicit error
- `RAGOptimizer` adjustments do not affect `ExecutionMode`, tier escalation, or safety thresholds

**Determinism:**
- All existing Phase 10 tests pass (12 passed, 1 skipped)
- New governance test covers all 10 integrated phases
- W10-EMBEDDING-HS-DIGEST stable across runs
- Replay engine uses 1536-dim synthetic vectors (no reshaping)

**Result:** Phase 10 reaches 100% structural closure with full OpenAI `text-embedding-3-large` activation across all HS injection points — elevated from "activated feature" to **sovereign infrastructure primitive**.
