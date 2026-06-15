# ADR-055 — Embedding Model Enforcement at Collection Boundary

**Status**: Accepted (implemented)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/L4_state/utils/client/chroma_client.py`, `tools/generate/ingestion/validate_collection.py`, `agentic_core/embeddings/embedding_factory.py`, all `tools/ingestion/ingest_*.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W1.3
**Relates-to**: ADR-018 (ChromaDB canonical), ADR-046 (Rerank revival), sibling plan `chromadb-bge-retrieval-hardening-e9aa09`

**Current-state note (2026-06-15):** Implemented by Chroma collection metadata checks in `agentic_core/L4_state/utils/client/chroma_client.py` and the BGE runtime path, with Chroma behavior, BGE runtime, and vector DB routing tests.

---

## Context

The repo's embedding pipeline currently has a **soft-versioning** posture:

- `agentic_core.embeddings.embedding_factory.create_deterministic_cache_key` includes `embedder_identity` (provider, model, dimensions, normalization, chunking) in the **cache key** so cached vectors never serve a query under a different embedder. ✅
- `SovereignChromaClient.get_collection` stamps `embedding_model` and `embedding_dim` into Chroma collection metadata on `get_or_create`. ✅
- `tools/generate/ingestion/validate_collection.py` reads that metadata at audit time and **warns** on mismatch. ⚠️
- Nothing **fails the write** when the active embedder disagrees with the collection's stamped model.

Concrete failure mode reproducible today:

1. A 1024-d BGE-M3 collection exists. `metadata.embedding_model = "BAAI/bge-m3"`, `embedding_dim = 1024`.
2. An operator runs an ingest path that constructs an `OpenAIEmbeddingClient(model="text-embedding-3-large", dimensions=1536)`.
3. `collection.add(embeddings=...)` accepts the 1536-d vectors. The HNSW index now contains co-mingled 1024-d and 1536-d embeddings under the same collection.
4. Subsequent queries return mathematical garbage. No exception raised. Validator logs a warning that operators usually do not see in CI.

The cache key prevents **read** corruption from cached vectors. It does **not** prevent **write** corruption when a fresh embedder is plumbed into a wrong-model collection.

Sibling plan `chromadb-bge-retrieval-hardening-e9aa09` §2.2 documents that `ingest_code.py` **stamps** `embedding_model = "fallback_hash_384"` while `SovereignChromaClient.embed_texts` actually computes 1024-d BGE-M3 vectors — the provenance metadata is wrong on entry today, which is one symptom of this same gap.

## Decision

Promote embedding-model enforcement from **soft (warn)** to **hard (fail-closed)** at every collection-write boundary.

### Normative Requirements

1. **EmbeddingProvenanceMismatchError** — new exception in `agentic_core/embeddings/`. Subclasses `RuntimeError`. Carries `expected_model`, `expected_dim`, `actual_model`, `actual_dim`, `collection_name`, `caller_module`.

2. **Pre-write check** — `SovereignChromaClient.add_documents` SHALL, before calling `collection.add`:
   - Read `collection.metadata` for `embedding_model` and `embedding_dim`.
   - Compare against the **active embedder identity** resolved from the bound embedder (or, when caller passes pre-computed `embeddings=`, against the manifest the caller is REQUIRED to also pass — see §3).
   - On mismatch: raise `EmbeddingProvenanceMismatchError`. Never silently coerce.
   - On collection with empty/missing metadata (legacy): one-shot stamp + log a `LEGACY_COLLECTION_STAMPED` event; subsequent writes are checked normally.

3. **Caller-supplied `embeddings=` requires manifest** — when the caller bypasses `embed_texts` and passes pre-computed vectors, they MUST also pass `embedder_identity: dict` (provider, model, dim, normalization, chunking). Missing manifest → `EmbeddingProvenanceMismatchError`. Closes the late-chunking and multi-head sidecar paths against silent dim drift.

4. **First-write pins dim** — when a collection is first populated, its `embedding_dim` is locked. Subsequent writes that produce a different dim raise. Tracked in collection metadata under `dim_locked_at` (ISO-8601 UTC).

5. **`ingest_*.py` provenance correction** — every ingest script SHALL stamp `embedding_model` and `embedding_dim` in chunk metadata using the **active embedder's** values, not a hardcoded constant. CI gate `check_ingest_provenance.py` enforces this by AST-walking ingest scripts and rejecting hardcoded model strings outside an allowlist.

6. **Validator escalation** — `tools/generate/ingestion/validate_collection.py` `--strict` mode (default ON in CI) treats every existing warning as a failure. Operators get a one-knob downgrade for local dev via `VALIDATE_COLLECTION_STRICT=0`.

7. **Telemetry** — every raise emits an OTel span attribute set: `gen_ai.embedding.provenance_mismatch=true`, `gen_ai.embedding.expected_model`, `gen_ai.embedding.actual_model`. Pipes into `otel_mcp.anomalies` for cross-session visibility.

### Non-Goals

- Migrating existing co-mingled collections — handled by a separate one-shot reindex plan that depends on this ADR landing first.
- Cross-dim interoperability (Matryoshka) — handled by ADR-057. Matryoshka sizes of the same base model SHALL still stamp **distinct** `embedding_dim` values and live in **distinct** collections (or sub-collections).
- Multi-head BGE-M3 (dense + sparse + ColBERT) dimension accounting — handled by ADR-056. Each head is treated as its own embedder identity and stored in its own sidecar.

## Consequences

**Positive**
- Eliminates the entire class of silent vector-dim corruption that sibling plan `e9aa09` documents across at least 3 call sites.
- Makes retrieval-quality regression attributable — every vector in a collection is provably produced by one embedder identity.
- Enables safe model rotation: swap model → CI gate fails on first write → operators know to reindex before shipping.
- RAGAS-style eval harnesses (W5.1) gain a precondition they can assume rather than probe defensively.

**Negative / costs**
- Every `add_documents` call pays a one-time metadata read per collection per client lifetime (amortizable via client-side memoization; negligible).
- Legacy call sites that relied on silent behavior break loudly. Migration cost: ~5 ingest scripts + 2 test fixtures per sibling-plan evidence.
- CI build time +~15s for the new AST gate.

**Risks**
- **R1 — Legacy collections without metadata.** Mitigation: one-shot stamping path with `LEGACY_COLLECTION_STAMPED` telemetry event; explicit 30-day burn-down window tracked in Wave/Phase Convergence.
- **R2 — Operator confusion on first-write dim-lock.** Mitigation: error message includes remediation: *"Collection `X` is empty but its metadata stamps `dim=1024`. To reindex under a different dim, first `delete_collection('X')` or reindex into a new name."*
- **R3 — CI gate false positives on legitimate multi-embedder tests.** Mitigation: allowlist in `check_ingest_provenance.py` scoped to `tests/` and `tools/eval/`.

## Alternatives Considered

1. **Keep soft-warn.** Status quo. Rejected — sibling plan documents active production-impacting drift.
2. **Validate at query time only.** Too late; corruption already persisted.
3. **Pin model in collection name (e.g. `code_chunks__bge-m3-1024`).** Self-documenting but fragments the namespace and breaks backward compatibility with ADR-018. Deferred — may be revisited for Matryoshka per-dim sub-collections under ADR-057.
4. **Use Chroma's native embedding function hook.** Ties us to ChromaDB's lifecycle; our embedder needs to live above Chroma per ADR-018 §Rationale and the embedding-sovereignty guard. Rejected.

## Validation

CI green defined as:
1. `check_ingest_provenance.py` passes — no hardcoded model strings outside allowlist.
2. `pytest tests/unit/agentic_core/L4_state/utils/client/test_chroma_client_behavior.py::test_provenance_mismatch_raises` passes — new test asserting `EmbeddingProvenanceMismatchError` on dim mismatch.
3. `tools/generate/ingestion/validate_collection.py --strict` returns exit 0 on all current canonical collections after one-shot legacy stamping.

Rollback: revert the pre-write check in `SovereignChromaClient` and set `VALIDATE_COLLECTION_STRICT=0` in CI. The exception class and telemetry attributes stay — they are non-breaking additive.

## Surface Map — BGE-M3 and BAAI Models in This Repo

Three distinct BAAI model surfaces exist in the codebase. They share a vendor prefix but
are **independent concerns** and must not be conflated.

| Surface | Model | Files | Dimension | Status | Governed by |
|---|---|---|---|---|---|
| **Dense embedder** | `BAAI/bge-m3` | `agentic_core/embeddings/bge_runtime.py`, `tools/embedders/bge_m3_embedder.py`, `tools/indexing/populate_apps_qna_index.py` | 1024-d | Active (apps_qna index populated 2026-05-05) | **This ADR** (ADR-055) |
| **Cross-encoder reranker** | `BAAI/bge-reranker-v2-m3` | `agentic_core/knowledge/retrieval/bge_reranker_adapter.py`, `apps_qna/router/reranker.py`, `apps_qna/engines/router/reranker.py` | N/A (scores) | Active (fail-soft passthrough if unavailable) | ADR-046 (Rerank revival) |
| **Multi-head (dense + sparse + ColBERT)** | `BAAI/bge-m3` (extended output) | `agentic_core/embeddings/bge_runtime.py` (dense head only today) | 1024-d dense; sparse TBD; ColBERT TBD | Proposed — gated on `BGE_MULTI_HEAD=1`; not default | ADR-056 |

**Key invariant**: ADR-055 enforcement (`PROVENANCE_ENFORCED_COLLECTIONS`) applies only to the
**dense embedder surface**. The cross-encoder reranker does not write to ChromaDB collections
and is not subject to this ADR. Multi-head enforcement will be added in a future ADR-056 amendment
when the multi-head path ships.

Added 2026-05-05 per plan `bge-m3-gap-closure-c8f3a2` W2.2.

## References

- ADR-018 (ChromaDB canonical vector store)
- ADR-046 (Rerank revival — reranker chain assumes consistent embedding identity)
- ADR-056 (BGE-M3 multi-head integration — dense + sparse + ColBERT)
- Plan `chromadb-bge-retrieval-hardening-e9aa09` §2.2 (embedding-path defects)
- Plan `bge-m3-gap-closure-c8f3a2` W2.2 (surface map addition), W3.1 (hard-fail impl)
- `agentic_core/embeddings/embedding_factory.py::create_deterministic_cache_key`
- `agentic_core/embeddings/exceptions.py::EmbeddingProvenanceMismatchError`
- `agentic_core/L4_state/utils/client/chroma_client.py::SovereignChromaClient`
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
