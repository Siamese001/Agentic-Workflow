---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\embedding-hardening-plan-b6d7e6.md'
original_relative_path: 'embedding-hardening-plan-b6d7e6.md'
source_sha256: c92148963bb388f2eec79740e44502f0d0a2eaee068734ba364b9c4b453017a3
recovered_status: LOST_RECOVERED
last_commit: 'afefe5d59e4'
last_commit_date: '2026-03-09 13:06:46 -0400'
created_date: '2026-02-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# OpenAI Embedding Integration Hardening Plan

Seven hardening improvements to eliminate known bypass debt, structurally prevent embedding influence on routing decisions, and enforce deterministic, privacy-safe embedding behavior.

---

## H-1: Eliminate `tiktoken` Bypass Debt in `hardening_mixin.py`

**Gap:** `agentic_core/mixins/hardening_mixin.py:187` uses `import tiktoken` directly for token counting. This is in `KNOWN_EMBEDDING_BYPASS_DEBT` but carries no expiry — it becomes a permanent bypass lane.

**Fix:** Extract token counting into a `TokenCountAdapter` in `agentic_core/embeddings/` that:
- Wraps `tiktoken` internally (single point of import)
- Is allowed by the AST scanner's allowlist (explicit exact-path entry)
- `hardening_mixin.py` calls `TokenCountAdapter.count_tokens()` — no direct `tiktoken` import

**Result:** bypass debt ceiling drops 2 → 1 → 0 as both known entries are resolved.

---

## H-2: Promote AST Scanner from "Detects" to "Blocking CI"

**Gap:** `test_ast_scanner_detects_embedding_bypass` prints EMBEDDING-BYPASS-DEBT stats but only *fails* if `found > ceiling`. It does not block on any positive `found` count.

**Fix — two-part:**

1. **Replace soft ceiling with hard zero-tolerance** in `test_no_new_embedding_bypass_violations`:
   - Drop `KNOWN_EMBEDDING_BYPASS_DEBT` set entirely once H-1 is resolved
   - Replace `assert found <= ceiling` with `assert found == 0` with message `"direct embedding SDK import detected — route through embedding_factory"`

2. **Extend scanner rules** (AST-based, in `test_phase10_embedding_non_mutation.py`):
   - Add `tiktoken` to forbidden imports (currently present) — confirm ceiling goes to 0 after H-1
   - Add `faiss` direct import outside `system_learning/engines/local_faiss_store.py`
   - Add `openai.Embedding` / `openai.embeddings` call-site detection (not just import)
   - Allowlist format: `{"path": "agentic_core/embeddings/embedding_factory.py", "sha256": "<hash>"}` — cryptographically bound

---

## H-3: Pin Embedder Identity into Replay Key and Determinism Digest

**Gap:** `EmbeddingServiceFactory.replay_key()` still uses `hf_repo`/BGE metadata. `OpenAIEmbeddingClient.get_replay_metadata()` returns `version: "1.0"` (not pinned to response-observed dimension). `DeterministicReplayEngine` synthetic cases use 8-dim toy vectors — not shape-compatible with 1536-dim production embeddings.

**Fix — three files:**

1. **`agentic_core/embeddings/embedding_factory.py`** — `get_replay_metadata()`:
   - Add `normalization_policy: "l2"` (OpenAI vectors are pre-normalized)
   - Add `chunking_policy: "none"` (full-text, no chunking)
   - Add `observed_dim: int` field populated from first API response
   - `pack_hash` must incorporate `observed_dim` so dimension swap breaks the hash

2. **`system_learning/engines/retrieval_profile.py`** — `RetrievalProfile`:
   - `primary_embedder_id = "openai/text-embedding-3-large"`
   - `embedding_dim = 1536`
   - `similarity_cutoff = 0.75`
   - Add `normalization_policy: str = "l2"` field to `to_canonical_json()` so digest reflects it

3. **`system_learning/engines/deterministic_replay_engine.py`** — synthetic cases:
   - Replace 8-dim toy vectors with 1536-dim zero-padded unit vectors
   - Or parametrize `dim` from `RetrievalProfile.embedding_dim` so cases are always shape-consistent

---

## H-4: Structural Embedding Output Non-Influence

**Gap:** Phase 10 tests *assert* non-mutation but nothing in the type system prevents it. `GovernedPayload` is `@dataclass(frozen=True)` but `c0_context: str` is mutable at assembly time — a future caller could pass embedding output directly into `i0_instructional`.

**Fix — two parts:**

1. **`EmbeddingArtifact` type guard** (`system_learning/types/embedding_artifact.py`):
   - Add `@dataclass(frozen=True)` with field `influence_class: Literal["C0_INFORMATIONAL"] = "C0_INFORMATIONAL"`
   - Add `assert_non_authoritative()` method that raises if artifact is used in a non-C0 slot

2. **`AirlockAssembler.assemble()`** (`agentic_core/L0_routing/engines/assembly_stage.py`):
   - Add `c0_context_source: Literal["static", "embedding_artifact"] = "static"` parameter
   - When `"embedding_artifact"`: assert `c0_context` was produced from `EmbeddingArtifact.influence_class == "C0_INFORMATIONAL"`
   - **Sealed decision record**: routing/tier/safety decisions (captured in `manifest_hash`) are computed from `s0_system + i0_instructional + u0_user_prompt` **only** — `c0_context` is excluded from the routing hash but included in the full manifest hash
   - This is mechanically enforced: a separate `routing_hash` field computed from the non-C0 slots

---

## H-5: Kill-Switch at Every HS Injection Point

**Gap:** `EMBEDDING_ENABLED` is checked at factory init and `EmbeddingServiceFactory.get_or_disabled()`. Individual HS injection points (HS-1 through HS-6) in production code do not re-check the kill-switch before calling the factory.

**Fix:**

1. **`embedding_factory.py`** — add `EmbeddingFactory.is_enabled() -> bool` class method (reads same env var)
2. **Each HS injection point** wraps embedding call with:
   ```python
   if not EmbeddingFactory.is_enabled():
       _emit_disabled_audit_signal()
       return <neutral_value>
   ```
3. **`_emit_disabled_audit_signal()`** — logs exactly one structured line per call site:
   ```
   EMBEDDING_DISABLED: site=<hs_id> component=<class> ts=<utc_epoch>
   ```
   This gives ops a clear signal that embedding is off at each seam.
4. **No silent heuristic fallback**: if disabled, return `None` / empty — not a degraded similarity score.

**Files touched:** `agentic_core/embeddings/embedding_factory.py`, each HS injection site.

---

## H-6: Deterministic Caching + Stable Float Handling

**Gap:** No canonical cache key defined for embedding results. `MetaLearningEmbeddingService` re-embeds the same query text on every call. `PatternAnalysisEngine` distance threshold uses Euclidean on raw floats — platform BLAS may affect results.

**Fix:**

1. **Cache key construction** (in `embedding_factory.py` or a new `EmbeddingCache`):
   - Key = `SHA-256(canonical_utf8(text) + "|" + provider + "|" + model + "|" + str(dimensions))`
   - No wall-clock, no random — fully deterministic
   - Cache stored in-process only (no disk persistence) — kill-switch respects it

2. **Stable float seam** in `EmbeddingServiceFactory.retrieve()`:
   - Add explicit `query_vector.astype(np.float32)` before dot product (already present but document as contract)
   - Add `np.round(scores, 6)` (already present) — document as determinism contract in docstring
   - Tie-breaker: `(score_round6 DESC, content_hash ASC)` — already present; add assertion in test

3. **`PatternAnalysisEngine`** — switch from Euclidean to cosine distance:
   - Cosine distance = `1 - cosine_similarity` — platform-independent on normalized vectors
   - New threshold: `0.25` cosine distance (= `0.75` similarity) for 1536-dim OpenAI space
   - Normalize input vectors with eps-guard before clustering

---

## H-7: Privacy + Data-Boundary Controls at the Embedding Seam

**Gap:** No field allowlist, no redaction, and raw text could be logged.

**Fix — new `EmbeddingInputGuard`** in `agentic_core/embeddings/embedding_input_guard.py`:

1. **Field allowlist** — only these fields may be embedded:
   - `u0_user_prompt`, `failure_signal.error_message`, `pattern_text`, `rag_query`
   - Any other field → `EmbeddingInputViolation` (hard fail)

2. **Redaction step** before any `embed_batch()` call:
   - Strip API keys (`sk-...`, `Bearer ...`)
   - Strip emails, UUIDs in sensitive positions
   - Strip anything matching the sovereign config secret patterns

3. **Logging contract**:
   - FORBIDDEN: `logger.info(f"Embedding: {text}")` — log text content
   - ALLOWED: `logger.info(f"Embedding: hash={sha256(text)[:16]} size={len(text)} model={model}")`
   - AST scanner rule: detect `logger.*` calls containing embedding variable names with raw text

4. **Test**: `test_embedding_input_guard` in `test_phase10_embedding_non_mutation.py` — verify redaction strips secrets before embedding call reaches factory

---

## Implementation Sequence

| Step | Hardening | Risk | Files |
|---|---|---|---|
| 1 | H-1: `TokenCountAdapter`, remove `tiktoken` from bypass debt | Low | 2 |
| 2 | H-2: Scanner zero-tolerance + cryptographic allowlist | Low | 1 |
| 3 | H-3: Replay key + `RetrievalProfile` + replay engine dims | Low | 3 |
| 4 | H-5: Kill-switch at each HS seam + audit signal | Low | 2 |
| 5 | H-6: Cache key + float contract + cosine distance | Low | 3 |
| 6 | H-7: `EmbeddingInputGuard` + redaction + log contract | Medium | 2 |
| 7 | H-4: `EmbeddingArtifact` type guard + routing hash split | Medium | 3 |

---

## Acceptance Criteria
- `EMBEDDING-BYPASS-DEBT: found=0` printed by scanner (no KNOWN entries)
- `test_no_new_embedding_bypass_violations`: `assert found == 0` (hard zero)
- `RetrievalProfile.profile_digest` changes (model upgrade reflected)
- `EmbeddingServiceFactory.replay_key()` includes `provider=openai` + `observed_dim`
- `EMBEDDING_DISABLED` audit signal logged when kill-switch off, at each HS seam
- Cache key is deterministic: same text + model → same cache key across runs
- `EmbeddingInputGuard.guard(text)` strips secrets before embed call
- Logger never contains raw embedded text (AST-verified)
- All existing Phase 10 tests still pass (12 passed, 1 skipped)
