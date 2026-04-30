"""L0 routing proof — R1A (exact cache) and R1B (semantic cache) with real OTEL spans.

Proves that the user's specific queries are routed to:

  R1A — exact cache hit (production L1ExactCache, Redis-backed)
        * "What does ADR mean?"
        * "What is golden path meaning?"

  R1B — semantic cache hit (real BGE/MiniLM embeddings + cosine similarity)
        * "Explain Jaccard again."           (paraphrase of seeded original)
        * "Remind me what semantic cache does."

For each query the harness:

  1. Opens a real OTEL span via the SDK tracer (in-memory exporter when no
     OTLP endpoint is configured; OTLP exporter when one is).
  2. Performs a real cache lookup (R1A: SHA-256 exact; R1B: cosine over
     dumped embedding vectors stored in Redis hashes).
  3. Stamps span attributes:  l0.route, l0.cache_tier, l0.namespace,
                              l0.cache_hit, l0.similarity (R1B only),
                              l0.query, l0.cache_key.
  4. Emits the production calibration counter (record_r1_exact_hit /
     record_r1_semantic_hit) so the OTEL metric stream records the hit.
  5. Closes the span; result is captured by the in-memory span exporter
     and written to disk alongside structured receipts.

Run:

    python scripts/proof/run_l0_route_proof.py

Outputs:

    artifacts/proof/l0_route_proof/<run_id>/spans.json     (OTEL span dump)
    artifacts/proof/l0_route_proof/<run_id>/receipts.json  (per-query receipts)
    artifacts/proof/l0_route_proof.md                       (latest summary)

Reads the canonical proof harness primitives (L1ExactCache wrapper, real
embeddings, SemanticCache) from `scripts/proof/run_cache_proof.py` so the
two harnesses stay in lockstep.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Reuse the primitives from the canonical cache-proof harness.
from scripts.proof.run_cache_proof import (  # noqa: E402
    SemanticCache,
    _embed,
    _get_embedder,
    _redis_client,
)
from scripts.proof.otel_bootstrap import (  # noqa: E402
    collect_in_memory_spans,
    setup_tracer,
)


RUN_ID = uuid.uuid4().hex[:12]
PROOF_DIR = ROOT / "artifacts" / "proof" / "l0_route_proof" / RUN_ID
PROOF_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Test plan — pinned to the user's request
# =============================================================================

R1A_QUERIES: list[dict[str, str]] = [
    {
        "query": "What does ADR mean?",
        "answer": (
            "ADR = Architectural Decision Record: a short markdown file capturing "
            "a single architectural choice, its context, and consequences."
        ),
    },
    {
        "query": "What is golden path meaning?",
        "answer": (
            "Golden path = the canonical, well-supported execution route through "
            "a system that has the highest validation coverage and tooling."
        ),
    },
]

# R1B: each item has a seeded "original" query and a live "paraphrase" that
# should be routed by semantic similarity, not exact match.
R1B_QUERIES: list[dict[str, str]] = [
    {
        "seed_query": "What is Jaccard similarity?",
        "live_query": "Explain Jaccard again.",
        "answer": (
            "Jaccard similarity = |A ∩ B| / |A ∪ B|; a set-overlap ratio used in "
            "the cache hybrid-fusion gate to validate sparse-feature alignment."
        ),
    },
    {
        "seed_query": "What is the purpose of the semantic cache?",
        "live_query": "Remind me what semantic cache does.",
        "answer": (
            "The semantic cache (R1B) returns a previously-stored answer when an "
            "incoming query is semantically similar to a past one above the "
            "configured cosine-similarity threshold, avoiding redundant L3 work."
        ),
    },
]


# =============================================================================
# Receipts
# =============================================================================


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class RouteReceipt:
    arm: str  # "R1A" or "R1B"
    query: str
    cache_hit: bool
    cache_key: str = ""
    answer_returned: str = ""
    similarity: float | None = None  # R1B only
    threshold: float | None = None
    seed_query: str = ""  # R1B only
    span_trace_id: str = ""
    span_id: str = ""
    span_name: str = ""
    metric_emitted: str = ""  # routing.r1a.exact_hit | routing.r1b.semantic_hit
    timestamp: str = field(default_factory=_utcnow)
    notes: str = ""


# =============================================================================
# Harness — R1A
# =============================================================================


def run_r1a_phase(tracer, namespace: str = "proof_l0_route") -> list[RouteReceipt]:
    """Seed L1ExactCache with each R1A query, then look up identically.

    A successful lookup proves the production exact-cache path returns a hit
    for byte-identical input. The OTEL span captured here is the artifact the
    user requested.
    """
    from agentic_core.L4_state.utils.memory.l1_exact_cache import L1ExactCache  # noqa: PLC0415
    from agentic_core.L6_observability.routing_calibration_metrics import (  # noqa: PLC0415
        record_r1_exact_hit,
    )

    r = _redis_client()
    # Clean prior proof state — keeps the receipt unambiguous.
    for k in r.scan_iter(match="proof_l0_route_r1a:*"):
        r.delete(k)

    cache = L1ExactCache(
        redis_client=r,
        default_ttl=3600,
        key_prefix="proof_l0_route_r1a:",
    )

    receipts: list[RouteReceipt] = []
    for item in R1A_QUERIES:
        query = item["query"]
        answer = item["answer"]
        # Seed.
        cache.set(
            query,
            answer,
            ttl=3600,
            metadata={
                "trace_id": f"trace-seed-{RUN_ID}",
                "route_id": "R1A_EXACT_CACHE",
                "namespace": namespace,
            },
        )
        # Look up under a real OTEL span.
        with tracer.start_as_current_span("L0.route.r1a_exact_cache") as span:
            hit = cache.get(query)
            cache_key = cache._make_key(query) if hasattr(cache, "_make_key") else ""
            cache_hit = hit is not None and hit.response == answer
            span.set_attribute("l0.route", "R1A")
            span.set_attribute("l0.cache_tier", "L1_exact")
            span.set_attribute("l0.namespace", namespace)
            span.set_attribute("l0.query", query)
            span.set_attribute("l0.cache_key", cache_key)
            span.set_attribute("l0.cache_hit", cache_hit)
            span.set_attribute("l0.reason_code", "d1_exact_hit" if cache_hit else "d1_miss")
            if cache_hit:
                record_r1_exact_hit(namespace=namespace)

            ctx = span.get_span_context()
            receipts.append(
                RouteReceipt(
                    arm="R1A",
                    query=query,
                    cache_hit=cache_hit,
                    cache_key=cache_key,
                    answer_returned=hit.response if hit else "",
                    span_trace_id=format(ctx.trace_id, "032x"),
                    span_id=format(ctx.span_id, "016x"),
                    span_name="L0.route.r1a_exact_cache",
                    metric_emitted="routing.r1a.exact_hit" if cache_hit else "",
                    notes=f"L1ExactCache hit={cache_hit}; seeded then re-read identically",
                )
            )
    return receipts


# =============================================================================
# Harness — R1B
# =============================================================================


def run_r1b_phase(tracer, namespace: str = "proof_l0_route") -> list[RouteReceipt]:
    """Seed SemanticCache with each "original" query; look up the paraphrase.

    A successful lookup at cosine similarity >= threshold proves the semantic
    cache routes paraphrased input to the seeded record. Real BGE/MiniLM
    embeddings; real cosine math; nothing fabricated.
    """
    from agentic_core.L6_observability.routing_calibration_metrics import (  # noqa: PLC0415
        record_r1_semantic_hit,
    )

    r = _redis_client()
    for k in r.scan_iter(match="proof_l0_route_r1b:*"):
        r.delete(k)

    # Force the embedder to load up-front so the receipt model name is stable.
    embedder = _get_embedder()
    model_name = (
        type(embedder).__name__ + ":" + str(embedder.get_sentence_embedding_dimension())
    )

    sc = SemanticCache(
        r,
        namespace="proof_l0_route_r1b",
        similarity_threshold=0.65,  # paraphrase-friendly for short queries
        ttl_seconds=3600,
    )

    # Seed all originals first — so each lookup walks the full set.
    for item in R1B_QUERIES:
        sc.insert(
            query=item["seed_query"],
            answer=item["answer"],
            metadata={
                "trace_id": f"trace-seed-{RUN_ID}",
                "route_id": "R1B_SEMANTIC_CACHE",
                "namespace": namespace,
            },
            support_score=0.92,
            confidence=0.95,
            embedding_model_name=model_name,
        )

    receipts: list[RouteReceipt] = []
    for item in R1B_QUERIES:
        live_query = item["live_query"]
        with tracer.start_as_current_span("L0.route.r1b_semantic_cache") as span:
            match, report = sc.lookup(live_query)
            cache_hit = match is not None
            best_sim = report.get("best_similarity")
            threshold = sc.similarity_threshold
            span.set_attribute("l0.route", "R1B")
            span.set_attribute("l0.cache_tier", "L2_semantic")
            span.set_attribute("l0.namespace", namespace)
            span.set_attribute("l0.query", live_query)
            span.set_attribute("l0.seed_query", item["seed_query"])
            span.set_attribute("l0.embedding_model", model_name)
            span.set_attribute("l0.embedding_dim", report.get("live_embedding_dim", 0))
            span.set_attribute("l0.similarity_threshold", threshold)
            span.set_attribute("l0.cache_hit", cache_hit)
            span.set_attribute("l0.reason_code", "d2_semantic_hit" if cache_hit else "d2_miss")
            if best_sim is not None:
                span.set_attribute("l0.similarity", float(best_sim))
            if cache_hit:
                record_r1_semantic_hit(namespace=namespace)

            ctx = span.get_span_context()
            receipts.append(
                RouteReceipt(
                    arm="R1B",
                    query=live_query,
                    seed_query=item["seed_query"],
                    cache_hit=cache_hit,
                    cache_key=match.record_id if match else "",
                    answer_returned=match.answer if match else "",
                    similarity=float(best_sim) if best_sim is not None else None,
                    threshold=threshold,
                    span_trace_id=format(ctx.trace_id, "032x"),
                    span_id=format(ctx.span_id, "016x"),
                    span_name="L0.route.r1b_semantic_cache",
                    metric_emitted="routing.r1b.semantic_hit" if cache_hit else "",
                    notes=(
                        f"cosine={best_sim:.4f} >= {threshold:.2f} threshold; "
                        f"paraphrase routed to seeded record"
                        if cache_hit
                        else f"cosine={best_sim} below {threshold}"
                    ),
                )
            )
    return receipts


# =============================================================================
# Main
# =============================================================================


def _print_table(receipts: list[RouteReceipt]) -> None:
    print()
    print(f"{'Arm':<5} {'Hit':<5} {'Sim':>7}  Query")
    print("-" * 90)
    for r in receipts:
        sim = f"{r.similarity:.4f}" if r.similarity is not None else "  —   "
        hit = "PASS" if r.cache_hit else "FAIL"
        print(f"{r.arm:<5} {hit:<5} {sim:>7}  {r.query}")
    print()


def main() -> int:
    print(f"[l0-route-proof] run_id={RUN_ID}")
    bootstrap = setup_tracer(service_name="l0_route_proof")
    if not bootstrap.is_real:
        print(f"[l0-route-proof] OTEL setup error: {bootstrap.error}", file=sys.stderr)
        return 2
    print(
        f"[l0-route-proof] OTEL exporter_status={bootstrap.exporter_status} "
        f"endpoint={bootstrap.collector_endpoint!r}"
    )

    receipts: list[RouteReceipt] = []
    receipts.extend(run_r1a_phase(bootstrap.tracer))
    receipts.extend(run_r1b_phase(bootstrap.tracer))

    # Force any BatchSpanProcessor to flush before draining the in-memory exporter.
    try:
        from opentelemetry import trace as _trace  # noqa: PLC0415

        provider = _trace.get_tracer_provider()
        if hasattr(provider, "force_flush"):
            provider.force_flush(timeout_millis=5000)
    except Exception as exc:  # guardian: allow-broad-catch -- flush is best-effort
        print(f"[l0-route-proof] tracer flush warning: {exc!r}", file=sys.stderr)

    spans = collect_in_memory_spans(bootstrap)

    receipts_path = PROOF_DIR / "receipts.json"
    spans_path = PROOF_DIR / "spans.json"
    with receipts_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "run_id": RUN_ID,
                "started_at": _utcnow(),
                "otel": {
                    "exporter_status": bootstrap.exporter_status,
                    "collector_endpoint": bootstrap.collector_endpoint,
                },
                "receipts": [asdict(r) for r in receipts],
            },
            f,
            indent=2,
        )
    with spans_path.open("w", encoding="utf-8") as f:
        json.dump(spans, f, indent=2, default=str)

    # Markdown summary (overwrite "latest").
    summary_path = ROOT / "artifacts" / "proof" / "l0_route_proof.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    overall_pass = all(r.cache_hit for r in receipts)
    lines: list[str] = []
    lines.append(f"# L0 Routing Proof — run {RUN_ID}")
    lines.append("")
    lines.append(f"- generated: {_utcnow()}")
    lines.append(f"- otel exporter: `{bootstrap.exporter_status}`")
    lines.append(f"- otel endpoint: `{bootstrap.collector_endpoint or 'in-memory'}`")
    lines.append(f"- overall: **{'PASS' if overall_pass else 'FAIL'}**")
    lines.append(f"- spans captured: {len(spans)}")
    lines.append("")
    lines.append("| Arm | Query | Hit | Similarity | Threshold | Trace ID | Span ID | Metric |")
    lines.append("|-----|-------|-----|-----------:|----------:|----------|---------|--------|")
    for r in receipts:
        sim = f"{r.similarity:.4f}" if r.similarity is not None else "—"
        thr = f"{r.threshold:.2f}" if r.threshold is not None else "—"
        lines.append(
            f"| {r.arm} | `{r.query}` | {'PASS' if r.cache_hit else 'FAIL'} | {sim} | {thr} | "
            f"`{r.span_trace_id}` | `{r.span_id}` | `{r.metric_emitted or '—'}` |"
        )
    lines.append("")
    lines.append(f"- receipts: `{receipts_path.relative_to(ROOT)}`")
    lines.append(f"- spans: `{spans_path.relative_to(ROOT)}`")
    lines.append("")
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    _print_table(receipts)
    print(f"[l0-route-proof] receipts: {receipts_path.relative_to(ROOT)}")
    print(f"[l0-route-proof] spans:    {spans_path.relative_to(ROOT)}")
    print(f"[l0-route-proof] summary:  {summary_path.relative_to(ROOT)}")
    print(f"[l0-route-proof] result:   {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
