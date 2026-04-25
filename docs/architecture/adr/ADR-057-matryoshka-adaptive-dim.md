# ADR-057 — Matryoshka / Adaptive-Dimension Embeddings

**Status**: Proposed
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/embeddings/bge_runtime.py`, `agentic_core/embeddings/embedding_factory.py`, `agentic_core/L4_state/utils/client/chroma_client.py`, `config/retrieval/retrieval_plan.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W2.2
**Relates-to**: ADR-018, ADR-055 (model enforcement), ADR-056 (multi-head), sibling plan `e9aa09`

---

## Context

Every embedding in the repo is stored at BGE-M3's native **1024-d**. No tier trades fidelity for latency or storage. This produces three observed frictions:

1. **Cold paths pay interactive costs.** Background anomaly triage, nightly audit scans, and offline analytics run against the same 1024-d HNSW as the interactive Cascade loop. 400 ms of HNSW traversal is irrelevant when the caller is an interactive agent but wasteful when the caller is a batch job iterating over 50 K candidates.
2. **Memory pressure on the ChromaDB host.** The largest collection (`code_chunks` per sibling plan `e9aa09`) holds ~100 K chunks × 1024 × 4 bytes ≈ 400 MB of float32 vectors in RAM when loaded. Scaling the corpus 5× pushes past a 2 GB working set for a single collection. Matryoshka dim-truncation lets the same content live at 256-d for a 4× memory cut with minimal recall loss (per Matryoshka Representation Learning: recall@100 drops <2 % going from 1024-d to 256-d on BGE-M3-scale models).
3. **Router has nothing to negotiate.** The future agentic router (W6.2) needs a knob to trade fidelity for latency per query SLO. If every collection is pinned at 1024-d, the router is reduced to "query or don't."

Matryoshka Representation Learning (Kusupati et al., 2022) trains an embedding so that **truncating to the first K dimensions still produces a valid, L2-meaningful vector**. BGE-M3 is trained with this property across at least {128, 256, 512, 1024}.

## Decision

Promote embedding dimension to a **first-class tier axis**, with BGE-M3 Matryoshka truncation as the mechanism.

### Normative Requirements

1. **Dim tier catalog** — canonical tiers for the repo:

   | Tier | Dim | Intended use | Recall@20 floor vs 1024-d baseline |
   |---|---:|---|---|
   | `hot-interactive` | 1024 | Cascade C0 live loop, chat retrieval | 1.00 (baseline) |
   | `warm-analytics` | 512 | Session-scoped analytics, scorer features | ≥ 0.97 |
   | `cold-batch` | 256 | Nightly audit, drift detection, bulk similarity | ≥ 0.93 |
   | `tiny-prefilter` | 128 | Candidate generation before warm/hot rerank | ≥ 0.85 |

   These floors are enforced by the W5.1 golden-set eval harness. A tier whose recall drops below its floor fails the ADR-055 model-enforcement gate.

2. **Collection-per-dim topology** — ChromaDB collections are **single-dim** (ADR-055 §4 locks `embedding_dim` on first write). Supporting N tiers means N collections per corpus, named `<base>__<dim>` (e.g. `code_chunks__256`, `code_chunks__512`, `code_chunks__1024`). Default when dim suffix is omitted: 1024 (back-compat).

3. **Truncation is derived, not recomputed** — `bge_runtime.bge_embed_multi` produces the 1024-d dense head. Lower-dim tiers are produced by **slicing** the first N components and re-L2-normalizing, not by re-encoding. CI gate `check_matryoshka_determinism.py` asserts that `slice_then_norm(bge_embed("x"), k) == bge_embed_tier("x", k)` bitwise for each tier.

4. **Retrieval plan selects tier** — `RetrievalPlan` (see `agentic_core/knowledge/retrieval/retrieval_plan.py`) gains `dim_tier: Literal["hot-interactive","warm-analytics","cold-batch","tiny-prefilter"]` with default `hot-interactive`. Callers that don't care get current behavior. The future agentic router (W6.2) sets it per query SLO.

5. **Cascade prefilter pattern** — a canonical two-step pattern is documented for large-corpus queries:
   ```
   Step 1: query tiny-prefilter (128-d) for top-500 candidates   (fast, broad)
   Step 2: re-score that top-500 with hot-interactive (1024-d)   (accurate)
   Step 3: (optional) cross-encoder rerank per ADR-046
   ```
   Cuts hot-dim HNSW traversal from full-corpus scale to a bounded 500. Empirically cheaper than a flat 1024-d HNSW above ~200K vectors.

6. **Storage accounting** — the per-tier collection is additive. For corpora where `tiny-prefilter` is unused, operators simply do not populate its collection. Multi-tier population is opt-in per corpus, tracked in `config/retrieval/retrieval_tiers.yaml` (new).

### Non-Goals

- Different **models** per tier (e.g. `text-embedding-3-large` at 3072-d for hot, BGE-M3 at 1024-d for warm). Cross-model Matryoshka is research-grade; this ADR is intra-model only.
- Dynamic-dim-per-query without pre-indexed tiers. Would require on-the-fly re-indexing; out of scope.
- Automatic tier selection. The router in W6.2 owns that policy; this ADR only wires the mechanism.

## Consequences

**Positive**
- Router-ready tiering — W6.2 can trade latency for recall on a per-query basis with a measured budget.
- 4× memory cut on cold-batch workloads with a documented <7 % recall penalty.
- Prefilter pattern scales corpus size past the 200 K-vector HNSW sweet spot without degrading hot-path latency.
- Matryoshka is derivation-only: no new forward-pass cost, no new model.

**Negative / costs**
- Storage amplification on multi-tier corpora. Worst case (all four tiers): +1.44× storage vs 1024-d alone (1024 + 512 + 256 + 128 = 1920; 1920/1024 = 1.88, minus overhead → ≈1.5-1.6× total). Most corpora will populate ≤2 tiers.
- Operational surface area: more collection names to keep straight. Mitigated by the `<base>__<dim>` convention + retrieval-tier config.
- Eval harness complexity — the golden-set run must now measure per-tier recall rather than a single number.

**Risks**
- **R1 — Truncate-then-normalize not bitwise-determined.** Mitigation: the CI gate checks it; if it ever fails, we block the ADR at its validation step.
- **R2 — Operators pick the wrong tier.** Mitigation: default is always `hot-interactive`; tiering is opt-in; `retrieval_tiers.yaml` documents intended use.
- **R3 — Sibling plan `e9aa09` dual-store consolidation must complete first.** Before multi-tier collections are created, there must be **one** store path per ADR-018. Otherwise 4 tiers × 2 paths = 8 inconsistent artifacts.
- **R4 — BGE-M3 Matryoshka quality below published numbers on code corpus.** The MRL paper targets general text; code retrieval is an out-of-distribution domain. Mitigation: W5.1 golden set includes code-specific queries; recall floors in §1 are verified, not assumed.

## Alternatives Considered

1. **Stay single-dim.** Router has no knob; cold paths overpay. Rejected.
2. **Switch to OpenAI `text-embedding-3-large` with Matryoshka truncation (1024/1536/3072).** Supports native dim truncation but violates ADR-018 (BGE-M3 pin) and adds API dependency on hot path. Deferred; may be a separate ADR for opt-in "premium" tier.
3. **PCA / quantization instead of Matryoshka.** Lossier than Matryoshka (which is trained-in) and adds a fit step. Rejected.
4. **Per-tier collection renamed via suffix convention only (no retrieval-plan field).** Encodes tier in names; all callers have to know the suffix. Rejected — brittle and hides the tier from metrics.

## Validation

- `pytest tests/unit/agentic_core/embeddings/test_matryoshka.py` — slice-then-norm determinism across tiers.
- `tools/eval/retrieval_abcd_harness.py` extended to sweep `dim_tier` alongside `RERANKER`. Recall floors per §1 are blocking.
- Storage report under `docs/reports/plans/matryoshka-storage-audit.md` generated by a one-shot `tools/eval/report_tier_storage.py` after rollout.

Rollback: delete non-1024 per-tier collections; revert `RetrievalPlan` to ignore `dim_tier`. 1024-d collections are untouched — rollback is fully reversible.

## References

- Kusupati, Bhatt, Rege, *et al.* — *Matryoshka Representation Learning* (NeurIPS 2022)
- Chen et al., *BGE M3-Embedding* (2024) §Multi-Granularity
- OpenAI, *New and improved embedding models* (Jan 2024) — text-embedding-3 Matryoshka
- In-repo: `agentic_core/knowledge/retrieval/retrieval_plan.py`
- Sibling plan: `chromadb-bge-retrieval-hardening-e9aa09` (store consolidation prereq)
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
