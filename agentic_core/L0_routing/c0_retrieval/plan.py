"""C0.1 RETRIEVAL PLAN — bounded search plan.

Spec: C0 Context Engine.md lines 183-258. No fetching here; this is the plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .preflight import C0PreflightStatus, EvidenceStandard
from .route_contract import L1PlanContract, RouteContract
from .verdicts import (
    EXACTNESS_REQUIRED,
    FreshnessClass,
    RetrievalMode,
    SourceClass,
    SupportTarget,
)


@dataclass(frozen=True)
class GraphBounds:
    """Spec lines 231-240 — bounded graph expansion."""

    max_hops: int = 1
    max_parent_expansion: int = 2
    max_child_expansion: int = 2
    relation_filter: tuple[str, ...] = ()  # GraphRelation values; empty = all

    def __post_init__(self) -> None:
        if self.max_hops < 0:
            raise ValueError("max_hops must be >= 0")
        if self.max_parent_expansion < 0 or self.max_child_expansion < 0:
            raise ValueError("expansion bounds must be >= 0")


@dataclass(frozen=True)
class Budgets:
    """Spec lines 231-240 — SLO/token/latency/cost envelope."""

    max_k: int = 20
    max_token_context: int = 4000
    max_latency_ms: int = 5000
    max_cost_tier: str = "standard"
    max_refine_attempts: int = 1
    max_source_classes: int = 7

    def __post_init__(self) -> None:
        if self.max_k <= 0:
            raise ValueError("max_k must be positive")
        if self.max_token_context <= 0:
            raise ValueError("max_token_context must be positive")
        if self.max_latency_ms <= 0:
            raise ValueError("max_latency_ms must be positive")
        if self.max_refine_attempts < 0:
            raise ValueError("max_refine_attempts must be >= 0")
        if self.max_source_classes <= 0:
            raise ValueError("max_source_classes must be positive")


@dataclass(frozen=True)
class DenseQuerySpec:
    """Spec lines 291-294 — dense lane parameters."""

    query_text: str
    embed_model_id: str = ""
    top_k: int = 20
    similarity_threshold: float = 0.0  # 0..1

    def __post_init__(self) -> None:
        if not self.query_text.strip():
            raise ValueError("dense query_text required")
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be in [0,1]")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")


@dataclass(frozen=True)
class SparseQuerySpec:
    """Spec lines 296-299 — sparse/BM25 lane parameters."""

    terms: tuple[str, ...]
    must_include: tuple[str, ...] = ()  # exact-match required
    boost_phrases: tuple[str, ...] = ()
    top_k: int = 20

    def __post_init__(self) -> None:
        if not self.terms and not self.must_include:
            raise ValueError("sparse query needs terms or must_include")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")


@dataclass(frozen=True)
class MetadataFilters:
    """Spec lines 301-303 — metadata filter set."""

    tenant_id: str
    region: str = ""
    source_types: tuple[SourceClass, ...] = ()
    authors: tuple[str, ...] = ()
    versions: tuple[str, ...] = ()
    created_after: str = ""  # ISO-8601
    created_before: str = ""
    data_classes: tuple[str, ...] = ()
    extra: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("MetadataFilters.tenant_id is required")


@dataclass(frozen=True)
class CachePolicy:
    """Spec lines 305-308 — cache reuse rules."""

    allow_cache: bool = False
    max_cache_age_seconds: int = 0  # 0 = no cache
    require_lineage: bool = True  # cached entries must include retrieval lineage
    invalidate_on_freshness: tuple[FreshnessClass, ...] = ()

    def __post_init__(self) -> None:
        if self.allow_cache and self.max_cache_age_seconds <= 0:
            raise ValueError("allow_cache=True requires max_cache_age_seconds > 0")


@dataclass(frozen=True)
class RetrievalPlan:
    """Spec lines 242-248 — output of C0.1.

    Frozen, replay-stable. Carries every parameter Fetch needs.
    """

    plan_id: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str
    support_target: SupportTarget
    evidence_standard: EvidenceStandard
    freshness_class: FreshnessClass
    source_classes: tuple[SourceClass, ...]
    allowed_sources: tuple[SourceClass, ...]
    disallowed_sources: tuple[SourceClass, ...]
    retrieval_modes: tuple[RetrievalMode, ...]
    dense_query_spec: DenseQuerySpec | None
    sparse_query_spec: SparseQuerySpec | None
    metadata_filters: MetadataFilters
    cache_policy: CachePolicy
    graph_bounds: GraphBounds
    budgets: Budgets
    weak_support_policy: str = "refine_once"  # refine_once|refine_max|abstain|reroute
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("RetrievalPlan.plan_id required")
        if not self.source_classes:
            raise ValueError("RetrievalPlan.source_classes must be non-empty")
        if not self.retrieval_modes:
            raise ValueError("RetrievalPlan.retrieval_modes must be non-empty")
        if self.weak_support_policy not in ("refine_once", "refine_max", "abstain", "reroute"):
            raise ValueError(f"invalid weak_support_policy: {self.weak_support_policy!r}")
        # Spec C0.I5 — exact targets MUST include sparse or metadata lane.
        if self.support_target in EXACTNESS_REQUIRED:
            if not (
                RetrievalMode.SPARSE in self.retrieval_modes
                or RetrievalMode.METADATA in self.retrieval_modes
                or RetrievalMode.HYBRID in self.retrieval_modes
            ):
                raise ValueError(
                    f"support_target={self.support_target.value} requires sparse "
                    f"or metadata or hybrid mode (C0.I5)",
                )
        # No fetching. No source escape.
        for s in self.allowed_sources:
            if s in self.disallowed_sources:
                raise ValueError(f"source {s.value!r} is both allowed and disallowed")


def _default_modes_for_target(target: SupportTarget) -> tuple[RetrievalMode, ...]:
    """Spec C0.I5: exact targets need sparse; semantic targets benefit from dense."""
    if target in EXACTNESS_REQUIRED:
        return (RetrievalMode.HYBRID, RetrievalMode.SPARSE, RetrievalMode.METADATA)
    if target == SupportTarget.ROOT_CAUSE_RANKING:
        return (RetrievalMode.HYBRID, RetrievalMode.GRAPH, RetrievalMode.METADATA)
    if target == SupportTarget.COMPARISON:
        return (RetrievalMode.HYBRID, RetrievalMode.METADATA)
    return (RetrievalMode.HYBRID, RetrievalMode.DENSE)


def build_retrieval_plan(
    *,
    route: RouteContract,
    plan_contract: L1PlanContract,
    preflight: C0PreflightStatus,
    plan_id: str,
    dense_query: DenseQuerySpec | None = None,
    sparse_query: SparseQuerySpec | None = None,
) -> RetrievalPlan:
    """Convert L1/L0 intent + preflight into a bounded RetrievalPlan."""
    if not preflight.eligible:
        raise ValueError(
            f"build_retrieval_plan called with ineligible preflight: "
            f"{preflight.blocked_reason}",
        )
    sources = preflight.allowed_source_classes
    metadata = MetadataFilters(
        tenant_id=route.tenant_scope,
        region=route.region,
        source_types=sources,
        data_classes=route.allowed_data_classes,
    )
    bounds = GraphBounds(
        max_hops=route.max_hops,
        max_parent_expansion=route.max_parent_expansion,
        max_child_expansion=route.max_child_expansion,
    )
    budgets = Budgets(
        max_k=route.max_k,
        max_token_context=route.max_token_context,
        max_latency_ms=route.max_latency_ms,
        max_cost_tier=route.max_cost_tier,
        max_refine_attempts=route.max_refine_attempts,
        max_source_classes=route.max_source_classes,
    )
    cache_policy = CachePolicy(
        allow_cache=route.freshness_class in (FreshnessClass.STATIC, FreshnessClass.SLOW),
        max_cache_age_seconds=86400 if route.freshness_class == FreshnessClass.STATIC else 0,
    )
    if dense_query is None:
        dense_query = DenseQuerySpec(query_text=plan_contract.query_spec or plan_contract.task_spec)
    return RetrievalPlan(
        plan_id=plan_id,
        route_replay_key=route.route_replay_key,
        policy_hash=route.policy_hash,
        blueprint_hash=route.blueprint_hash,
        support_target=route.support_target,
        evidence_standard=preflight.evidence_standard,
        freshness_class=route.freshness_class,
        source_classes=sources,
        allowed_sources=route.allowed_sources or sources,
        disallowed_sources=route.disallowed_sources,
        retrieval_modes=_default_modes_for_target(route.support_target),
        dense_query_spec=dense_query,
        sparse_query_spec=sparse_query,
        metadata_filters=metadata,
        cache_policy=cache_policy,
        graph_bounds=bounds,
        budgets=budgets,
        weak_support_policy="refine_once" if route.max_refine_attempts > 0 else "abstain",
    )


__all__ = [
    "Budgets",
    "CachePolicy",
    "DenseQuerySpec",
    "GraphBounds",
    "MetadataFilters",
    "RetrievalPlan",
    "SparseQuerySpec",
    "build_retrieval_plan",
]
