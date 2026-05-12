"""apps_research C0.3 graph adapter — W4N chroma-graphrag-lic-rg-research-f4a2e9.

W4N (no-core track) invariants enforced here:
  - This module does not call the graph traversal engine.
  - This module does not import from the L4 state layer.
  - This module MUST NOT write to L4, answer, route, or execute tools.
  - This module is CONFIG_PREPARED_ONLY — C0.3 adapter registry deferred.
  - ``build_research_graph_traverse_input()`` returns a typed dict; live
    ``GraphTraverseInput`` construction is deferred (C0.3 adapter registry not
    wired under no-core plan).
  - apps_research enables supersession_scan (max_hops=2) per no-core route-profile.
  - Embedding-model conflict (text-embedding-3-large / 3072-dim) is deferred to
    W5N; the chroma research store is not accessed in this file.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
    AmbiguousAnchorResolution,
    GraphAdapterHealth,
    GraphNeighbor,
    GraphRelationPath,
    GraphTraversalAdapter,
    ProjectionManifest,
    UnresolvedAnchorResolution,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
    AnchorCandidate,
    ResolvedGraphAnchor,
)


# ---------------------------------------------------------------------------
# W4N policy constants — must match apps_research route_profile.company_brief.v1.yaml
# ---------------------------------------------------------------------------

_GRAPH_SOURCE = "apps_research.company_brief_graph.v1"
_PROJECTION_VERSION = "v1.0.0"
_SNAPSHOT_POINTER = "apps_research::snapshot::placeholder"

RESEARCH_ALLOWED_RELATION_TYPES: tuple[str, ...] = (
    "SOURCE_AUTHORITY",
    "SOURCE_VERSION",
    "CONTRADICTS",
    "SUPERSEDES",
    "SUPERSEDED_BY",
    "EVIDENCE",
    "DERIVED_FROM",
)
RESEARCH_MAX_HOPS: int = 2
RESEARCH_MAX_NODES: int = 64
RESEARCH_MAX_EDGES: int = 128
RESEARCH_CONTRADICTION_SCAN_ENABLED: bool = True
RESEARCH_SUPERSESSION_SCAN_ENABLED: bool = True


# ---------------------------------------------------------------------------
# Pure builder — W4N entry-point for future C0.3 wiring
# ---------------------------------------------------------------------------


def build_research_graph_traverse_input(
    route_contract: Any,
    hydrated_candidates: list[Any],
) -> dict[str, Any]:
    """Build a GraphTraverseInput-compatible dict for apps_research.

    W4N: returns a typed dict — live ``GraphTraverseInput`` construction is
    deferred until C0.3 adapter registry is wired (requires agentic_core
    GENERIC_INFRA_EDIT).  This function does not invoke the traversal engine.

    Args:
        route_contract: Route-contract-like object or dict carrying the
            ``graph_traverse`` policy block (from the no-core route profile).
        hydrated_candidates: List of hydrated evidence candidates from C0.

    Returns:
        A dict with all fields required by ``GraphTraverseInput`` when the
        registry becomes live.  Safe to construct with zero side effects.
    """
    graph_policy = (
        route_contract.get("graph_traverse", {})
        if isinstance(route_contract, dict)
        else getattr(route_contract, "graph_traverse", {}) or {}
    )
    return {
        "app_id": "apps_research",
        "allowed_relation_types": list(
            graph_policy.get(
                "allowed_relation_types", list(RESEARCH_ALLOWED_RELATION_TYPES)
            )
        ),
        "max_hops": graph_policy.get("max_hops", RESEARCH_MAX_HOPS),
        "max_nodes": graph_policy.get("max_nodes", RESEARCH_MAX_NODES),
        "max_edges": graph_policy.get("max_edges", RESEARCH_MAX_EDGES),
        "contradiction_scan_enabled": graph_policy.get(
            "contradiction_scan_enabled", RESEARCH_CONTRADICTION_SCAN_ENABLED
        ),
        "supersession_scan_enabled": graph_policy.get(
            "supersession_scan_enabled", RESEARCH_SUPERSESSION_SCAN_ENABLED
        ),
        "hydrated_candidates": hydrated_candidates,
        "graph_adapter_ref": "apps_research.integrations.c0_graph_adapter",
        "live_wiring_deferred": True,
        "wiring_gate": "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED",
    }


# ---------------------------------------------------------------------------
# GraphTraversalAdapter implementation (stub — backend not live)
# ---------------------------------------------------------------------------


class ResearchGraphAdapter:
    """apps_research company-brief graph adapter for C0.3.

    W4N discipline:
      - Does not call the graph traversal engine.
      - Does not import from the L4 state layer.
      - MUST NOT write L4, answer, route, or execute tools.
      - Stub implementations — no live backend connected.
      - supersession_scan=True per no-core route-profile policy.
    """

    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution:
        return UnresolvedAnchorResolution(
            candidate=anchor_candidate,
            reason="apps_research graph adapter: stub — no live backend connected (W4N)",
        )

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]:
        return ()

    def get_relation_path(
        self,
        start_node_id: str,
        neighbor_node_id: str,
    ) -> GraphRelationPath:
        return GraphRelationPath(
            start_node_id=start_node_id,
            end_node_id=neighbor_node_id,
            relations=(),
            nodes=(start_node_id, neighbor_node_id),
        )

    def get_projection_manifest(self) -> ProjectionManifest:
        return ProjectionManifest(
            graph_source=_GRAPH_SOURCE,
            projection_version=_PROJECTION_VERSION,
            snapshot_pointer=_SNAPSHOT_POINTER,
            snapshot_built_at="1970-01-01T00:00:00Z",
            canonical_source_hash="stub-0000",
            is_stale=False,
        )

    def health_check(self) -> GraphAdapterHealth:
        return GraphAdapterHealth(
            healthy=True,
            backend=_GRAPH_SOURCE,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
        )


def get_graph_adapter() -> GraphTraversalAdapter:
    """Entry-point consumed by ``resolve_graph_adapter()`` (future wiring).

    W4N: C0.3 adapter registry not wired under no-core plan.
    Returns a fresh ``ResearchGraphAdapter`` instance each call.
    """
    return ResearchGraphAdapter()
