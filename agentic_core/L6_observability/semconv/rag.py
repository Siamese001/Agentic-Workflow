"""RAG OpenTelemetry semantic-convention constants — ADR-062 SSOT.

Every retrieval-stage emitter in the codebase MUST import attribute keys and
span names from this module. CI gate ``check_otel_semconv_use`` rejects raw
``gen_ai.retrieval.*`` string literals outside this module and its tests.

The naming follows the OpenTelemetry GenAI working draft (2024–2025) for the
``gen_ai.*`` prefix; retrieval-specific extensions diverge where the upstream
schema does not yet cover the surface (multi-head, reflective loop, drift).

Stage spans (children of ``SPAN_QUERY``) emit in this order when present:

    SPAN_QUERY_TRANSFORM  (ADR-058)
    SPAN_EMBED            (ADR-057 dim tier; ADR-056 multi-head)
    SPAN_SEARCH           (per-modality: dense / sparse / colbert)
    SPAN_FUSE             (RRF / weighted)
    SPAN_RERANK           (ADR-046 / ADR-056 late-interaction)
    SPAN_GRADE            (ADR-060 reflective loop)
    SPAN_EXPAND           (ADR-060 expansion strategies)

Single-pass retrieval emits a subset; the reflective loop emits the full set
≥ 1× per iteration.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Span names
# ---------------------------------------------------------------------------

SPAN_QUERY: Final[str] = "gen_ai.retrieval.query"
SPAN_QUERY_TRANSFORM: Final[str] = "gen_ai.retrieval.query_transform"
SPAN_EMBED: Final[str] = "gen_ai.retrieval.embed"
SPAN_SEARCH: Final[str] = "gen_ai.retrieval.search"
SPAN_FUSE: Final[str] = "gen_ai.retrieval.fuse"
SPAN_RERANK: Final[str] = "gen_ai.retrieval.rerank"
SPAN_GRADE: Final[str] = "gen_ai.retrieval.grade"
SPAN_EXPAND: Final[str] = "gen_ai.retrieval.expand"

ALL_SPAN_NAMES: Final[frozenset[str]] = frozenset(
    {
        SPAN_QUERY,
        SPAN_QUERY_TRANSFORM,
        SPAN_EMBED,
        SPAN_SEARCH,
        SPAN_FUSE,
        SPAN_RERANK,
        SPAN_GRADE,
        SPAN_EXPAND,
    }
)


# ---------------------------------------------------------------------------
# Common attributes (every retrieval span)
# ---------------------------------------------------------------------------

ATTR_RUN_ID: Final[str] = "gen_ai.retrieval.run_id"
ATTR_QUERY_HASH: Final[str] = "gen_ai.retrieval.query_hash"
ATTR_EMBEDDER_IDENTITY: Final[str] = "gen_ai.retrieval.embedder_identity"
ATTR_DIM_TIER: Final[str] = "gen_ai.retrieval.dim_tier"
ATTR_COLLECTION: Final[str] = "gen_ai.retrieval.collection"

COMMON_ATTRS: Final[frozenset[str]] = frozenset(
    {
        ATTR_RUN_ID,
        ATTR_QUERY_HASH,
        ATTR_EMBEDDER_IDENTITY,
        ATTR_DIM_TIER,
        ATTR_COLLECTION,
    }
)


# ---------------------------------------------------------------------------
# Per-stage attributes
# ---------------------------------------------------------------------------

# query_transform stage (ADR-058)
ATTR_TRANSFORM_NAME: Final[str] = "gen_ai.retrieval.transform_name"
ATTR_TRANSFORM_ID: Final[str] = "gen_ai.retrieval.transform_id"
ATTR_TRANSFORM_ROUTE: Final[str] = "gen_ai.retrieval.transform_route"
ATTR_BUDGET_USED_MS: Final[str] = "gen_ai.retrieval.budget_used_ms"
ATTR_FALLBACK: Final[str] = "gen_ai.retrieval.fallback"

# embed stage (ADR-056 / ADR-057)
ATTR_EMBED_HEAD: Final[str] = "gen_ai.retrieval.embed_head"
ATTR_LATENCY_MS: Final[str] = "gen_ai.retrieval.latency_ms"
ATTR_CACHE_HIT: Final[str] = "gen_ai.retrieval.cache_hit"

# search stage
ATTR_SEARCH_MODE: Final[str] = "gen_ai.retrieval.search_mode"
ATTR_TOP_K: Final[str] = "gen_ai.retrieval.top_k"
ATTR_SCORE_DIST_HASH: Final[str] = "gen_ai.retrieval.score_dist_hash"

# fuse stage
ATTR_FUSE_METHOD: Final[str] = "gen_ai.retrieval.fuse_method"
ATTR_FUSE_INPUTS: Final[str] = "gen_ai.retrieval.fuse_inputs"
ATTR_FUSE_OUTPUT_TOP_K: Final[str] = "gen_ai.retrieval.fuse_output_top_k"

# rerank stage (ADR-046)
ATTR_RERANKER_NAME: Final[str] = "gen_ai.retrieval.reranker_name"
ATTR_RERANK_PRE_FILTER_TOP_K: Final[str] = "gen_ai.retrieval.rerank_pre_filter_top_k"
ATTR_RERANK_OUTPUT_TOP_K: Final[str] = "gen_ai.retrieval.rerank_output_top_k"

# grade stage (ADR-060)
ATTR_GRADE_VERDICT_DIST: Final[str] = "gen_ai.retrieval.grade_verdict_dist"
ATTR_GRADER_IDENTITY: Final[str] = "gen_ai.retrieval.grader_identity"

# expand stage (ADR-060)
ATTR_EXPAND_STRATEGY: Final[str] = "gen_ai.retrieval.expand_strategy"
ATTR_LOOP_ITER: Final[str] = "gen_ai.retrieval.loop_iter"


# ---------------------------------------------------------------------------
# Outcome attributes (on parent SPAN_QUERY)
# ---------------------------------------------------------------------------

ATTR_OUTCOME: Final[str] = "gen_ai.retrieval.outcome"
ATTR_ITERATIONS: Final[str] = "gen_ai.retrieval.iterations"
ATTR_EVIDENCE_QUALITY: Final[str] = "gen_ai.retrieval.evidence_quality"
ATTR_COST_USD: Final[str] = "gen_ai.retrieval.cost_usd"

ATTR_LOOP_CAP_REASON: Final[str] = "gen_ai.retrieval.loop_cap_reason"
ATTR_PROVENANCE_MISMATCH: Final[str] = "gen_ai.embedding.provenance_mismatch"
ATTR_EXPECTED_MODEL: Final[str] = "gen_ai.embedding.expected_model"
ATTR_ACTUAL_MODEL: Final[str] = "gen_ai.embedding.actual_model"


# ---------------------------------------------------------------------------
# Outcome enum-likes (string literals, not enums — OTel attributes are str)
# ---------------------------------------------------------------------------

OUTCOME_CONVERGED: Final[str] = "converged"
OUTCOME_CAP: Final[str] = "cap"
OUTCOME_BUDGET_EXCEEDED: Final[str] = "budget_exceeded"
OUTCOME_ABSTAINED: Final[str] = "abstained"
OUTCOME_ERROR: Final[str] = "error"

VALID_OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        OUTCOME_CONVERGED,
        OUTCOME_CAP,
        OUTCOME_BUDGET_EXCEEDED,
        OUTCOME_ABSTAINED,
        OUTCOME_ERROR,
    }
)

EVIDENCE_STRONG: Final[str] = "strong"
EVIDENCE_WEAK: Final[str] = "weak"
EVIDENCE_NONE: Final[str] = "none"

VALID_EVIDENCE_QUALITIES: Final[frozenset[str]] = frozenset({EVIDENCE_STRONG, EVIDENCE_WEAK, EVIDENCE_NONE})

EMBED_HEAD_DENSE: Final[str] = "dense"
EMBED_HEAD_SPARSE: Final[str] = "sparse"
EMBED_HEAD_COLBERT: Final[str] = "colbert"

VALID_EMBED_HEADS: Final[frozenset[str]] = frozenset(
    {EMBED_HEAD_DENSE, EMBED_HEAD_SPARSE, EMBED_HEAD_COLBERT}
)

DIM_TIER_HOT: Final[str] = "hot-interactive"
DIM_TIER_WARM: Final[str] = "warm-analytics"
DIM_TIER_COLD: Final[str] = "cold-batch"
DIM_TIER_TINY: Final[str] = "tiny-prefilter"

VALID_DIM_TIERS: Final[frozenset[str]] = frozenset(
    {DIM_TIER_HOT, DIM_TIER_WARM, DIM_TIER_COLD, DIM_TIER_TINY}
)


__all__ = [
    # Span names
    "SPAN_QUERY",
    "SPAN_QUERY_TRANSFORM",
    "SPAN_EMBED",
    "SPAN_SEARCH",
    "SPAN_FUSE",
    "SPAN_RERANK",
    "SPAN_GRADE",
    "SPAN_EXPAND",
    "ALL_SPAN_NAMES",
    # Common attributes
    "ATTR_RUN_ID",
    "ATTR_QUERY_HASH",
    "ATTR_EMBEDDER_IDENTITY",
    "ATTR_DIM_TIER",
    "ATTR_COLLECTION",
    "COMMON_ATTRS",
    # Per-stage
    "ATTR_TRANSFORM_NAME",
    "ATTR_TRANSFORM_ID",
    "ATTR_TRANSFORM_ROUTE",
    "ATTR_BUDGET_USED_MS",
    "ATTR_FALLBACK",
    "ATTR_EMBED_HEAD",
    "ATTR_LATENCY_MS",
    "ATTR_CACHE_HIT",
    "ATTR_SEARCH_MODE",
    "ATTR_TOP_K",
    "ATTR_SCORE_DIST_HASH",
    "ATTR_FUSE_METHOD",
    "ATTR_FUSE_INPUTS",
    "ATTR_FUSE_OUTPUT_TOP_K",
    "ATTR_RERANKER_NAME",
    "ATTR_RERANK_PRE_FILTER_TOP_K",
    "ATTR_RERANK_OUTPUT_TOP_K",
    "ATTR_GRADE_VERDICT_DIST",
    "ATTR_GRADER_IDENTITY",
    "ATTR_EXPAND_STRATEGY",
    "ATTR_LOOP_ITER",
    # Outcome
    "ATTR_OUTCOME",
    "ATTR_ITERATIONS",
    "ATTR_EVIDENCE_QUALITY",
    "ATTR_COST_USD",
    "ATTR_LOOP_CAP_REASON",
    "ATTR_PROVENANCE_MISMATCH",
    "ATTR_EXPECTED_MODEL",
    "ATTR_ACTUAL_MODEL",
    # Enum-likes
    "OUTCOME_CONVERGED",
    "OUTCOME_CAP",
    "OUTCOME_BUDGET_EXCEEDED",
    "OUTCOME_ABSTAINED",
    "OUTCOME_ERROR",
    "VALID_OUTCOMES",
    "EVIDENCE_STRONG",
    "EVIDENCE_WEAK",
    "EVIDENCE_NONE",
    "VALID_EVIDENCE_QUALITIES",
    "EMBED_HEAD_DENSE",
    "EMBED_HEAD_SPARSE",
    "EMBED_HEAD_COLBERT",
    "VALID_EMBED_HEADS",
    "DIM_TIER_HOT",
    "DIM_TIER_WARM",
    "DIM_TIER_COLD",
    "DIM_TIER_TINY",
    "VALID_DIM_TIERS",
]
