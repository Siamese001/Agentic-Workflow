# ADR-062 — RAG OpenTelemetry Semantic Conventions + Drift Metric

**Status**: Accepted (implemented; drift alert artifacts available)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/L6_observability/`, `agentic_core/knowledge/retrieval/`, `agentic_core/L1_cognition/reasoning/`, `agentic_core/embeddings/`, `tools/eval/`
**Plan**: `.claude/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W5.3
**Relates-to**: ADR-055 (provenance telemetry), ADR-058 (transform telemetry), ADR-060 (reflective loop telemetry), ADR-061 (eval metrics)

**Current-state note (2026-06-15):** `agentic_core/L6_observability/semconv/rag.py`, `tools/eval/retrieval_drift.py`, and retrieval calibration manifest drift fields exist. `build_drift_alert()` and `write_drift_report()` now provide filesystem alert artifacts; automatic Notion writes are superseded by current filesystem-governance routing.

---

## Context

The repo emits OTel spans across retrieval today (per `agentic_core/L6_observability/utils/evaluation/*` and the embedding factory's identity stamping), but there is **no shared semantic-convention layer** for the retrieval surface. Each ADR in this plan adds its own attributes (`gen_ai.embedding.provenance_mismatch`, `gen_ai.query.transform_route`, `gen_ai.retrieval.loop_iter`, etc.) without a consolidated namespace, and the existing trace-grader at L6 cannot correlate them deterministically.

Two consequences:

1. Anomaly debugging of a single query requires reading code to know which spans matter — span discovery is ad-hoc.
2. Production-query **drift** (the corpus' growing distance from the queries hitting it) is not measured anywhere. ADRs 055/056/058/060 each promise drift-resilient behaviour but no signal proves they hold over weeks.

## Decision

Adopt a **RAG OpenTelemetry semantic-convention layer** under the `gen_ai.retrieval.*` namespace with five mandatory stage spans and a drift-metric pipeline.

### Normative Requirements

1. **Span hierarchy** — every retrieval call emits a parent span `gen_ai.retrieval.query` containing exactly these child spans (in order, when present):

   | Stage span name | Emitted when |
   |---|---|
   | `gen_ai.retrieval.query_transform` | ADR-058 transform fires (any non-identity) |
   | `gen_ai.retrieval.embed` | per dim-tier embedder pass (ADR-057) |
   | `gen_ai.retrieval.search` | per dense / sparse / late-interaction stage |
   | `gen_ai.retrieval.fuse` | RRF / score fusion across modalities |
   | `gen_ai.retrieval.rerank` | factory-resolved reranker fires (ADR-046, ADR-056) |
   | `gen_ai.retrieval.grade` | reflective loop grader (ADR-060) |
   | `gen_ai.retrieval.expand` | reflective loop expansion |

   Single-pass retrieval emits a subset; the reflective loop emits the full set ≥ 1× per iteration.

2. **Common attributes** (every span):
   - `gen_ai.retrieval.run_id` — same across stages of one query
   - `gen_ai.retrieval.query_hash` — sha256 of normalized query
   - `gen_ai.retrieval.embedder_identity` — per ADR-055 manifest
   - `gen_ai.retrieval.dim_tier` — per ADR-057 (`hot|warm|cold|tiny`)
   - `gen_ai.retrieval.collection` — fully-qualified Chroma collection name

3. **Per-stage attributes**:

   | Span | Required attributes |
   |---|---|
   | `query_transform` | `transform_name`, `transform_id`, `transform_route`, `budget_used_ms`, `fallback` |
   | `embed` | `head ∈ {dense,sparse,colbert}`, `latency_ms`, `cache_hit` |
   | `search` | `mode ∈ {dense,sparse,colbert}`, `top_k`, `latency_ms`, `score_dist_hash` |
   | `fuse` | `method ∈ {rrf,weighted}`, `inputs`, `output_top_k` |
   | `rerank` | `reranker_name`, `pre_filter_top_k`, `output_top_k`, `latency_ms`, `score_dist_hash`, `fallback` |
   | `grade` | `verdict_dist`, `latency_ms`, `grader_identity` |
   | `expand` | `strategy ∈ {hyde,step_back,decomposition,graph_hop,multi_query}`, `loop_iter` |

4. **Outcome attributes** (on parent `gen_ai.retrieval.query`):
   - `gen_ai.retrieval.outcome ∈ {converged, cap, budget_exceeded, abstained, error}`
   - `gen_ai.retrieval.iterations` (1 for single-pass)
   - `gen_ai.retrieval.evidence_quality ∈ {strong, weak, none}` (per ADR-060 ladder)
   - `gen_ai.retrieval.cost_usd` (best-effort sum of LLM costs across the loop)

5. **Constants module** — `agentic_core/L6_observability/semconv/rag.py` (new) declares all attribute names as Python constants. **All emitters must import from this module**; CI gate `check_otel_semconv_use.py` rejects raw `gen_ai.retrieval.*` string literals outside that module + its tests.

6. **Drift metric** — new pipeline `tools/eval/retrieval_drift.py`:

   - **Input** — every `gen_ai.retrieval.query` parent span over a 7-day rolling window (read via `mcp7_otel_spans_by_agent` or directly from the OTel store).
   - **Compute**:
     - `query_centroid_t` = L2-normalized mean of query embeddings (1024-d) for the window.
     - `corpus_centroid_collection` = pre-computed centroid stamped on the collection at ingest end (one new collection-metadata field, additive).
     - `drift_score = 1 - cosine(query_centroid_t, corpus_centroid_collection)`.
   - **Threshold** — `drift_score > 0.15` triggers a `[DRIFT-ALERT]` Notion row in Wave/Phase Convergence with the metric value, top divergent query themes (top-K queries furthest from corpus_centroid), and recommended action (re-ingest? expand corpus? add transform?).
   - **Cadence** — weekly, run by the same cron entry as ADR-061's full sweep.

7. **MCP integration** — `mcp7_otel_ingest_to_runtime_adg` is fed `gen_ai.retrieval.*` spans so the runtime ADG (per the static-vs-runtime ADG separation in canonical invariants §8) reflects observed retrieval flow alongside structural code flow. Read-back via `mcp7_otel_spans_by_agent` honors the agent class name `retrieval`.

### Non-Goals

- Replacing the existing `evaluation_record.py` evaluation telemetry. That handles agent-task evaluation; this ADR is retrieval-stage telemetry. Both flow into the same OTel collector.
- Defining semconv for generation-side spans (`gen_ai.completion.*`). Out of scope.
- Cost-tracking for non-LLM retrieval steps. The `cost_usd` attribute is best-effort and only meaningful when LLM calls fired.

## Consequences

**Positive**
- Single namespace + constants module = grep-discoverable, refactor-safe.
- Per-stage attribution makes anomaly debugging mechanical: which stage owns the latency / failure?
- Drift metric is the missing operational signal that connects ingest-side ADRs (045/055/056) to live retrieval health.
- Runtime-ADG integration enables `otel_mcp` as the canonical "what happened at runtime" gateway for retrieval, mirroring its existing agent-class coverage.

**Negative / costs**
- Span cardinality grows ~5× per query. Mitigated by sampling: 100 % for dev, 10 % nightly + always-on for queries marked `evidence_quality=weak|none`. Sampling rate operator-tunable.
- Adds a CI gate to enforce semconv constants. Small dev friction; pays back the first time a typo would have hidden a regression.
- Drift metric requires a new collection-metadata field (`corpus_centroid_v1`). Additive; ADR-055 enforcement re-stamps on next ingest cycle.

**Risks**
- **R1 — span volume saturates the OTel collector.** Mitigation: tunable sampling; aggregate stats sidecar (`gen_ai.retrieval.summary` only) when full spans disabled.
- **R2 — drift threshold mis-tuned.** Mitigation: first 30 days run advisory-only; threshold tuned against the empirically observed distribution of `drift_score` per corpus before alerts go live.
- **R3 — corpus centroid stale after partial re-ingest.** Mitigation: corpus_centroid is recomputed on every full re-ingest; partial re-ingest invalidates and recomputes lazily on next drift run.

## Validation

- `pytest tests/unit/agentic_core/L6_observability/semconv/test_rag_constants.py` — every emitter file imports from the constants module; no raw literals.
- `pytest tests/integration/test_retrieval_otel_pipeline.py` — issuing one query produces the expected span tree shape.
- One drift-run produces a `drift_score` value within `[0,1]` for each non-empty collection.
- Notion `[DRIFT-ALERT]` row posted on a synthetic-skew test corpus.

Rollback: disable the constants gate; emitters can fall back to raw strings. Drift cron entry can be disabled independently; spans continue to flow.

## Alternatives Considered

1. **Reuse OpenInference / OpenLLMetry conventions verbatim.** Their schema is generation-centric and missing reflective-loop / multi-head fields. We cherry-pick alignment where it exists (`gen_ai.*` prefix); diverge where retrieval-specific. Net: we adopt their **prefix** but extend their **schema**.
2. **Stamp drift inside the embedding factory rather than a separate cron.** Conflates ingest and observation; the centroid wants a corpus-level view that single-document writes don't have.
3. **No drift metric; rely on golden-set Recall@20 trend.** Necessary but not sufficient — golden set is frozen; production queries drift independently. Both signals are complementary.
4. **Use Prometheus instead of OTel.** Loses span-tree semantics; we already operate OTel via `otel_mcp`. Rejected.

## References

- OpenTelemetry GenAI semantic conventions (in-development working draft, 2024–2025)
- OpenInference schema (Arize)
- In-repo: `agentic_core/L6_observability/utils/evaluation/`, `tools/eval/retrieval_benchmark.py`
- Sibling: ADR-061 (golden-set harness consumes these spans for per-cell metrics)
- Parent plan: `.claude/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
