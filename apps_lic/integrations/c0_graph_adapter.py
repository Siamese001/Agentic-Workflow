"""apps_lic C0.3 graph adapter — live over the apps_rg shared proof SSOT (W2.1).

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W2.1). Supersedes the
W4N "no-core / stub" track: the core C0.3 adapter registry
(``agentic_core...c0_3_enhanced.adapter_registry.resolve_graph_adapter``) is a
generic dotted-path resolver — no agentic_core edit is needed to wire apps_lic.

Discipline preserved from W4N:
  - Read-only: does NOT mutate the graph, write L4, answer, route, or run tools.
  - Sources neighbours/anchors from the apps_rg ``augmented_skills_graph`` shared
    SSOT via :mod:`apps_lic.integrations.apps_rg_proof_bridge` (fail-soft: an
    unavailable shared graph yields empty results + unhealthy health_check, never
    a hard failure).
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
    AclStatus,
    AnchorCandidate,
    AnchorType,
    FreshnessStatus,
    ResolvedGraphAnchor,
)

from apps_lic.integrations.apps_rg_proof_bridge import (
    PERMISSION_ALLOW,
    AppsRgProofIndex,
    load_apps_rg_proof_index,
)


# ---------------------------------------------------------------------------
# W2 policy constants — must match apps_lic/config/domain_contract/route_profiles.yaml
# ---------------------------------------------------------------------------

# apps_lic projection identity (route-profile contract). The shared apps_rg
# graph is the UNDERLYING data source, surfaced via source_type / snapshot
# pointer / neighbor lineage — not by renaming this projection.
_GRAPH_SOURCE = "apps_lic.knowledge_graph.v1"
_PROJECTION_VERSION = "v1.0.0"
_WIRING_GATE = "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED"

LIC_ALLOWED_RELATION_TYPES: tuple[str, ...] = (
    "GOVERNED_BY",
    "OBSERVED_IN",
    "CONTRADICTS",
    "OWNED_BY",
    "REQUIRES",
)
LIC_MAX_HOPS: int = 2
LIC_MAX_NODES: int = 64
LIC_MAX_EDGES: int = 128
LIC_CONTRADICTION_SCAN_ENABLED: bool = True
LIC_SUPERSESSION_SCAN_ENABLED: bool = False

_DATA_CLASS = "EVIDENCE_DATA_ONLY"


# ---------------------------------------------------------------------------
# Pure builder — C0.3 traverse-input shape
# ---------------------------------------------------------------------------


def build_lic_graph_traverse_input(
    route_contract: Any,
    hydrated_candidates: list[Any],
) -> dict[str, Any]:
    """Build a GraphTraverseInput-compatible dict for apps_lic (static config shape).

    This is the route-input config builder (the W4N traverse-input contract);
    the *live* traversal is provided by :class:`LicGraphAdapter`. The shape stays
    static so the route-profile contract is stable.
    """
    graph_policy = (
        route_contract.get("graph_traverse", {})
        if isinstance(route_contract, dict)
        else getattr(route_contract, "graph_traverse", {}) or {}
    )
    return {
        "app_id": "apps_lic",
        "allowed_relation_types": list(
            graph_policy.get("allowed_relation_types", list(LIC_ALLOWED_RELATION_TYPES))
        ),
        "max_hops": graph_policy.get("max_hops", LIC_MAX_HOPS),
        "max_nodes": graph_policy.get("max_nodes", LIC_MAX_NODES),
        "max_edges": graph_policy.get("max_edges", LIC_MAX_EDGES),
        "contradiction_scan_enabled": graph_policy.get(
            "contradiction_scan_enabled", LIC_CONTRADICTION_SCAN_ENABLED
        ),
        "supersession_scan_enabled": graph_policy.get(
            "supersession_scan_enabled", LIC_SUPERSESSION_SCAN_ENABLED
        ),
        "hydrated_candidates": hydrated_candidates,
        "graph_adapter_ref": "apps_lic.integrations.c0_graph_adapter",
        "live_wiring_deferred": True,
        "wiring_gate": _WIRING_GATE,
    }


# ---------------------------------------------------------------------------
# GraphTraversalAdapter implementation (live over apps_rg shared SSOT)
# ---------------------------------------------------------------------------


def _node_type(node_id: str) -> str:
    return "skill" if str(node_id).startswith("skill_") else "fact"


def _skill_lineage(index: AppsRgProofIndex, node_id: str) -> tuple[str, ...]:
    proof = index.skills_by_id.get(node_id)
    return proof.fact_id_links if proof is not None else ()


def _authority_class(index: AppsRgProofIndex, node_id: str) -> str | None:
    proof = index.skills_by_id.get(node_id)
    if proof is None:
        return None
    return f"{proof.permission}:{proof.confidence_grade or 'NA'}"


class LicGraphAdapter:
    """apps_lic knowledge-graph adapter for C0.3, live over the apps_rg SSOT.

    Returns real approved proof-points (IDs + source lineage + permission) from
    the shared ``augmented_skills_graph``; empty/unresolved only when the shared
    SSOT is unavailable.
    """

    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution:
        _ = scope
        index = load_apps_rg_proof_index()
        value = str(anchor_candidate.anchor_value or "").strip()
        node_id = ""
        anchor_type = anchor_candidate.anchor_type
        if value in index.skill_to_node:
            node_id = index.skill_to_node[value]
            anchor_type = AnchorType.SERVICE
        elif value in index.fact_to_node:
            node_id = index.fact_to_node[value]
            anchor_type = AnchorType.DOCUMENT
        if not node_id:
            reason = (
                f"apps_lic graph: no node for anchor={value!r}"
                if index.available
                else "apps_lic graph: apps_rg shared proof SSOT unavailable"
            )
            return UnresolvedAnchorResolution(candidate=anchor_candidate, reason=reason)
        return ResolvedGraphAnchor(
            anchor_id=f"anchor:{node_id}",
            original_evidence_id=anchor_candidate.original_evidence_id,
            anchor_type=anchor_type,
            anchor_value=value,
            resolved_node_id=node_id,
            graph_source=_GRAPH_SOURCE,
            source_id=anchor_candidate.hint_source_id or node_id,
            source_version=index.graph_version,
            confidence=max(float(anchor_candidate.confidence), 0.55),
            resolution_reason="apps_rg.augmented_skills_graph exact match (shared SSOT)",
            acl_status=AclStatus.CLEARED,
        )

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]:
        _ = scope
        index = load_apps_rg_proof_index()
        allowed = {str(r).strip().upper() for r in relation_types if str(r).strip()}
        out: list[GraphNeighbor] = []
        for nb_id, rel, _eid, _direction in index.adjacency.get(node_id, ()):  # type: ignore[union-attr]
            if allowed and rel.upper() not in allowed:
                continue
            nb_type = _node_type(nb_id)
            lineage = _skill_lineage(index, nb_id) if nb_type == "skill" else (nb_id,)
            out.append(
                GraphNeighbor(
                    node_id=nb_id,
                    node_type=nb_type,
                    source_id=nb_id,
                    source_type=index.graph_source,
                    source_version=index.graph_version,
                    relation_type=rel,
                    relation_path=(node_id, rel, nb_id),
                    hop_distance=1,
                    tenant=None,
                    region=None,
                    data_class=_DATA_CLASS,
                    acl_status=AclStatus.CLEARED,
                    freshness_status=FreshnessStatus.FRESH,
                    confidence=0.6,
                    lineage_refs=lineage,
                    span_ref=None,
                    graph_source=_GRAPH_SOURCE,
                    projection_version=_PROJECTION_VERSION,
                    snapshot_pointer=index.snapshot_pointer,
                    payload_preview=None,
                    authority_class=_authority_class(index, nb_id),
                )
            )
            if len(out) >= max(1, limit):
                break
        return tuple(out)

    def get_relation_path(
        self,
        start_node_id: str,
        neighbor_node_id: str,
    ) -> GraphRelationPath:
        index = load_apps_rg_proof_index()
        for nb_id, rel, _eid, _direction in index.adjacency.get(start_node_id, ()):  # type: ignore[union-attr]
            if nb_id == neighbor_node_id:
                return GraphRelationPath(
                    start_node_id=start_node_id,
                    end_node_id=neighbor_node_id,
                    relations=(rel,),
                    nodes=(start_node_id, neighbor_node_id),
                )
        return GraphRelationPath(
            start_node_id=start_node_id,
            end_node_id=neighbor_node_id,
            relations=(),
            nodes=(start_node_id, neighbor_node_id),
        )

    def get_projection_manifest(self) -> ProjectionManifest:
        index = load_apps_rg_proof_index()
        return ProjectionManifest(
            graph_source=_GRAPH_SOURCE,
            projection_version=_PROJECTION_VERSION,
            snapshot_pointer=index.snapshot_pointer,
            snapshot_built_at="live" if index.available else "1970-01-01T00:00:00Z",
            canonical_source_hash=index.graph_digest or "unavailable",
            is_stale=not index.available,
            stale_reason="" if index.available else (index.load_error or "apps_rg shared SSOT unavailable"),
        )

    def health_check(self) -> GraphAdapterHealth:
        index = load_apps_rg_proof_index()
        return GraphAdapterHealth(
            healthy=index.available,
            backend=index.graph_source,
            latency_p50_ms=1.0 if index.available else 0.0,
            latency_p95_ms=5.0 if index.available else 0.0,
            last_error="" if index.available else index.load_error,
        )


def get_graph_adapter() -> GraphTraversalAdapter:
    """Entry-point consumed by ``resolve_graph_adapter()`` (generic registry)."""
    return LicGraphAdapter()


__all__ = [
    "LIC_ALLOWED_RELATION_TYPES",
    "LIC_MAX_EDGES",
    "LIC_MAX_HOPS",
    "LIC_MAX_NODES",
    "LicGraphAdapter",
    "build_lic_graph_traverse_input",
    "get_graph_adapter",
]
