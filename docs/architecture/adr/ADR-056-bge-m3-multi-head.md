# ADR-056 — BGE-M3 Multi-Head Integration (Dense + Sparse + ColBERT)

**Status**: Proposed
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/embeddings/bge_runtime.py`, `agentic_core/embeddings/embedding_factory.py`, `agentic_core/L4_state/utils/memory/bm25_store.py`, `agentic_core/L4_state/utils/client/chroma_client.py`, new `agentic_core/knowledge/retrieval/late_interaction_index.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W2.1
**Relates-to**: ADR-018, ADR-046 (cross-encoder rerank), ADR-055 (model enforcement)

---

## Context

The repo standardized on **BAAI/bge-m3** (ADR-018; `agentic_core/embeddings/bge_runtime.py:39`). BGE-M3 is a **multi-head** model: a single forward pass produces three embedding outputs simultaneously:

| Head | Output shape | Similarity metric | Canonical use |
|---|---|---|---|
| **Dense** | 1024-d float vector | cosine | ANN recall (current repo usage) |
| **Sparse (lexical)** | ~100-token-weight dict | lexical weighted overlap | BM25-style keyword recall |
| **ColBERT (multi-vector)** | N token vectors × 1024-d | MaxSim late interaction | Long-chunk fidelity, rerank |

Today only the **dense** head is used. The sparse and ColBERT outputs are discarded.

Implications of the status quo:

1. **BM25 is decoupled from the embedder.** `bm25_store.py` runs a classical rank-bm25 over tokenized text. That means retrieval rankings depend on **two** vocabularies — the BGE tokenizer (for dense) and the BM25 tokenizer (for sparse). Query terms that BGE tokenizes into subwords but BM25 splits on whitespace produce score-distribution drift invisible to operators. BGE-M3's native sparse head eliminates this drift by using the same tokenizer and token-importance weights the dense head already computed.
2. **Long chunks underperform.** Dense-pooled 1024-d vectors lose fine-grained intra-chunk detail on chunks >512 tokens. ColBERT's MaxSim scoring recovers that detail by matching per-token vectors between query and document. The cross-encoder reranker (ADR-046) partially covers this gap but at higher latency and a per-query model load.
3. **We pay the compute but throw it away.** The sparse and ColBERT outputs are a byproduct of the same forward pass; skipping them saves ~0 ms on GPU but forfeits the signal.

## Decision

Extend the repo's embedding pipeline to capture **all three** BGE-M3 heads, store each in its own index, and use them at the right stage of retrieval.

### Normative Requirements

1. **Multi-head embedder output** — `agentic_core/embeddings/bge_runtime.py` gains a new function `bge_embed_multi(text, *, heads=("dense","sparse","colbert"))` returning a `MultiHeadEmbedding` dataclass: `{dense: list[float], sparse: dict[str, float], colbert: list[list[float]]}`. The existing `bge_embed_query` and `bge_embed_batch` functions remain (dense-only) for backward compatibility.

2. **Dense head** — canonical ChromaDB collection (no change from ADR-018).

3. **Sparse head** — replaces the rank-bm25 computation inside `agentic_core/L4_state/utils/memory/bm25_store.py`. The store's public API (`add`, `query`) is unchanged; the internal scorer swaps from rank-bm25 to native BGE-M3 sparse weights with a Lucene-style `BM25` decay applied on top of the weights. Migration gate: one-shot reindex per collection; old rank-bm25 indexes retained for 30 days as fallback.

4. **ColBERT head** — new sidecar index under `agentic_core/knowledge/retrieval/late_interaction_index.py`:
   - Storage: flat parquet file per collection at `artifacts/chromadb/colbert/<collection>.parquet`, columns `{chunk_id, token_count, vectors_int8}` where `vectors_int8` is `int8`-quantized (saves 4× memory vs float32 with <1 % MaxSim accuracy loss per ColBERTv2).
   - Index structure: none for v1 (full scan over top-K candidates from stage 1). v2 may add PLAID or ColBERTv2-style cluster index once candidate fan-in justifies it.
   - MaxSim kernel: numpy-first implementation; torch path behind an optional-install.

5. **Stage wiring** — update `HybridRecallStage` + `reranker_factory.get_reranker()`:
   ```
   Stage 1a: dense ANN         → top-150 from Chroma
   Stage 1b: sparse weighted   → top-150 from BM25 store
   Stage 1c: RRF fuse 1a+1b    → top-200 deduped candidates
   Stage 2:  ColBERT MaxSim    → top-50 (late interaction)         ← NEW default
   Stage 3:  cross-encoder     → top-20 (ADR-046 BGE-reranker-v2)  ← unchanged
   ```
   Selection matrix driven by `RERANKER` env:
   - `auto`/`heuristic` — stages 1a+1b+1c+heuristic (current default)
   - `cross_encoder` — stages 1a+1b+1c+stage 3 (current opt-in)
   - `cross_encoder_late` — stages 1a+1b+1c+2+3 (NEW, highest quality)
   - `late_only` — stages 1a+1b+1c+2 (NEW, mid-tier)

6. **Embedder identity** — under ADR-055, each head is a distinct embedder identity:
   - `{provider:"bge-m3", head:"dense",   model:"BAAI/bge-m3", dim:1024, normalization:"l2"}`
   - `{provider:"bge-m3", head:"sparse",  model:"BAAI/bge-m3", dim:"var", normalization:"none"}`
   - `{provider:"bge-m3", head:"colbert", model:"BAAI/bge-m3", dim:1024, normalization:"l2", per_token:true}`
   Collections and sidecars each carry their head's identity in metadata; writes are fenced per ADR-055.

7. **Backward compatibility** — the dense-only path remains functional with no config change. Multi-head capture is gated behind `BGE_MULTI_HEAD=1` for rollout. Default flips to on after W5.1 golden-set validation confirms ≥ parity on dense-only metrics.

### Non-Goals

- Training or fine-tuning BGE-M3 — frozen model only.
- Supporting other multi-head embedders (Jina-v3, voyage-3-multilingual) in this ADR. The protocol is extensible; additional models are separate ADRs.
- Replacing the cross-encoder reranker — ColBERT and cross-encoder are complementary (different cost/quality points), not substitutes.

## Consequences

**Positive**
- BM25 drift closed. Sparse and dense produced by the same tokenizer + same forward pass.
- Long-chunk retrieval quality recovered via MaxSim without paying full cross-encoder latency on every query.
- Existing BGE-M3 GPU time fully utilized — same wall-clock cost, materially more retrieval signal.
- Opens the door to "rerank-free" tiers (`late_only`) for cost-sensitive queries.

**Negative / costs**
- ColBERT sidecar storage: ~200 bytes/token × ~500 tokens/chunk × 100K chunks ≈ 10 GB per collection at int8. Large but tractable; gated behind a per-collection opt-in.
- Sparse-head replacement requires one-shot reindex of BM25 stores (5 collections per sibling plan `e9aa09`).
- Numpy MaxSim on 200 candidates × 500 tokens × 1024-d is ~100 ms CPU; acceptable but tight against ADR-046's 250 ms P95 budget. Benchmark gate in W5.1.

**Risks**
- **R1 — int8 quantization loss on ColBERT.** Mitigation: W5.1 A/B compares int8 vs float32 on a 500-query golden set; rollback knob `COLBERT_DTYPE=float32` per collection.
- **R2 — sparse-head scores are not pre-normalized the way rank-bm25 is.** Mitigation: apply explicit min-max to [0,1] before RRF so fusion with dense-cosine stays well-conditioned.
- **R3 — `bge_runtime.py` currently caches a dense-only encoder instance.** Mitigation: extend the shared lock to wrap a multi-head encoder; process-level singleton unchanged.
- **R4 — Memory footprint on 32 GB GPU box.** BGE-M3 base is ~2.3 GB; multi-head adds no weight (same model). Sidecar ColBERT vectors live on disk; load top-K at rerank time only.

## Alternatives Considered

1. **Keep dense-only, lean on cross-encoder reranker.** Current posture. Concedes free retrieval signal and leaves BM25/dense tokenizer drift open.
2. **Replace BGE-M3 with separate models per head** (e.g. SPLADE for sparse, ColBERTv2 for late interaction). More weight to load, harder to keep identities aligned, and more caches to warm. Rejected — BGE-M3's co-trained heads are the simpler win.
3. **Use Chroma's sparse vector support (experimental).** Chroma's sparse index is not GA and couples storage to collection lifecycle. Prefer our own `bm25_store` swap for control and portability.
4. **Jina's `jina-embeddings-v3` multi-task heads.** Competitive benchmarks; but requires model swap + full reindex and violates ADR-018's pin on BGE-M3. Separate ADR if ever considered.

## Validation

- `pytest tests/unit/agentic_core/embeddings/test_bge_multi_head.py` — asserts three-head output shape, determinism, identity stamping.
- `tools/eval/retrieval_abcd_harness.py` extended to exercise `cross_encoder_late` and `late_only` modes alongside existing trio. Acceptance gate: Recall@20 on golden set ≥ dense-only baseline + 5 % for `late_only`, + 15 % for `cross_encoder_late`.
- Latency regression: P95 end-to-end retrieval stays under 800 ms for `cross_encoder_late` on 32 GB GPU box.

Rollback: `BGE_MULTI_HEAD=0` disables capture; stages fall back to current dense+rank-bm25+heuristic-or-cross-encoder chain. Sidecar parquet files are leave-in-place (ignored when the flag is off).

## References

- Chen et al., *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings* (2024)
- Santhanam et al., *ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction* (2022)
- Khattab & Zaharia, *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction* (SIGIR 2020)
- Cormack et al., *Reciprocal Rank Fusion* (SIGIR 2009)
- In-repo: `agentic_core/embeddings/bge_runtime.py`, `agentic_core/L4_state/utils/memory/bm25_store.py`
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
