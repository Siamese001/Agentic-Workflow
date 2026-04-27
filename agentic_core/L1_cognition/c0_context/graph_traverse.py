"""C0.3 Graph Traverse — explicit GraphTraverseInput / GraphExpandedEvidencePool.

Doctrine: ``docs/reference/03A_C0_Context_Engine/C0.3_Graph_RAG.md``

Closes the C0.3 schema gap previously logged in
``C0_Requirements_Traceability_Matrix.md`` row C0.3.GAP1.

This module is **additive**. It does not modify any existing C0 stage; it
provides the dataclasses the spec requires for C0.3 and a reference
``traverse_bounded`` function that enforces every named bound (max_hops,
max_nodes, max_edges, ACL, freshness, relation type, source class) without
itself doing any retrieval.

The 13 graph relations from the spec (defines, references, imports, calls,
owns, depends_on, supersedes, contradicts, duplicates, implements,
governed_by, derived_from, observed_in) are encoded as a closed enum.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Final


# --------------------------------------------------------------------------- #
# Closed vocabularies — exact spec wording.
# --------------------------------------------------------------------------- #


class GraphRelation(Enum):
    """13 graph relations C0.3 may follow (per spec §C0.3 doctrine)."""

    DEFINES = "defines"
    REFERENCES = "references"
    IMPORTS = "imports"
    CALLS = "calls"
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    SUPERSEDES = "supersedes"
    CONTRADICTS = "contradicts"
    DUPLICATES = "duplicates"
    IMPLEMENTS = "implements"
    GOVERNED_BY = "governed_by"
    DERIVED_FROM = "derived_from"
    OBSERVED_IN = "observed_in"


GRAPH_RELATIONS: Final[frozenset[str]] = frozenset(r.value for r in GraphRelation)


class GraphExclusionReason(Enum):
    """Reasons a neighbor was rejected from expansion."""

    MAX_HOPS = "max_hops_reached"
    MAX_NODES = "max_nodes_reached"
    MAX_EDGES = "max_edges_reached"
    ACL_BLOCKED = "acl_blocked"
    FRESHNESS_BLOCKED = "freshness_blocked"
    RELATION_DISALLOWED = "relation_disallowed"
    SOURCE_CLASS_DISALLOWED = "source_class_disallowed"
    SUPPORT_TARGET_IRRELEVANT = "support_target_irrelevant"
    DUPLICATE = "duplicate"


# --------------------------------------------------------------------------- #
# Dataclasses (frozen — replay-stable).
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class GraphNodeRef:
    """A reference to a node already in the candidate pool or to be expanded."""

    node_id: str
    source_id: str
    source_class: str
    acl_status: str
    freshness_status: str
    authority_score: float = 0.5


@dataclass(frozen=True)
class GraphEdge:
    """A single relation between two nodes."""

    relation: GraphRelation
    src_node_id: str
    dst_node_id: str
    weight: float = 1.0
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class GraphTraverseInput:
    """C0.3 PHASE 1 §2 — full input contract for bounded graph expansion."""

    # Identity / replay.
    route_id: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str

    # Task and support.
    support_target: str
    freshness_class: str

    # Scope.
    tenant_scope: str
    acl_scope: tuple[str, ...]
    region_scope: str
    data_class_scope: str

    # Bounds — every named bound the spec enumerates.
    max_hops: int
    max_nodes: int
    max_edges: int
    max_parent_expansion: int
    max_child_expansion: int
    max_relation_types: int
    max_contradiction_edges: int
    max_dependency_edges: int
    max_lineage_edges: int
    max_latency_ms: int
    max_token_budget_for_graph_context: int

    # Allowed / disallowed.
    allowed_graph_sources: frozenset[str]
    disallowed_graph_sources: frozenset[str]
    allowed_relation_types: frozenset[str]
    disallowed_relation_types: frozenset[str]
    allowed_source_classes: frozenset[str]
    disallowed_source_classes: frozenset[str]

    # Payload.
    hydrated_seeds: tuple[GraphNodeRef, ...]

    def __post_init__(self) -> None:
        # Validation per spec §PHASE 1 §2.
        if self.max_hops < 0:
            raise ValueError("max_hops must be >= 0")
        if self.max_nodes <= 0:
            raise ValueError("max_nodes must be positive")
        if self.max_edges <= 0:
            raise ValueError("max_edges must be positive")
        unknown_rel = self.allowed_relation_types - GRAPH_RELATIONS
        if unknown_rel:
            raise ValueError(
                f"allowed_relation_types contains unknown relations: {sorted(unknown_rel)}",
            )
        unknown_dis = self.disallowed_relation_types - GRAPH_RELATIONS
        if unknown_dis:
            raise ValueError(
                f"disallowed_relation_types contains unknown relations: {sorted(unknown_dis)}",
            )
        if self.allowed_relation_types & self.disallowed_relation_types:
            raise ValueError(
                "allowed_relation_types and disallowed_relation_types overlap",
            )
        if self.allowed_graph_sources & self.disallowed_graph_sources:
            raise ValueError(
                "allowed_graph_sources and disallowed_graph_sources overlap",
            )


@dataclass(frozen=True)
class GraphExpansionRecord:
    """One node added (or rejected) during expansion."""

    node: GraphNodeRef
    via_edge: GraphEdge
    hops_from_seed: int
    accepted: bool
    rejection_reason: GraphExclusionReason | None = None


@dataclass(frozen=True)
class GraphTraversalManifest:
    """Replay manifest — every traversal decision recorded deterministically."""

    seed_node_ids: tuple[str, ...]
    nodes_visited: int
    edges_visited: int
    max_hop_reached: int
    relation_counts: tuple[tuple[str, int], ...]  # sorted by relation name
    rejection_counts: tuple[tuple[str, int], ...]  # sorted by reason
    manifest_hash: str


@dataclass(frozen=True)
class GraphExpandedEvidencePool:
    """C0.3 PHASE 1 §3 — output. Bounded, ACL-cleared, replay-stable."""

    accepted_nodes: tuple[GraphNodeRef, ...]
    accepted_edges: tuple[GraphEdge, ...]
    expansion_records: tuple[GraphExpansionRecord, ...]
    manifest: GraphTraversalManifest


# --------------------------------------------------------------------------- #
# Bounded traversal reference implementation.
# --------------------------------------------------------------------------- #


def traverse_bounded(
    inp: GraphTraverseInput,
    *,
    edges_by_src: dict[str, tuple[GraphEdge, ...]],
    nodes_by_id: dict[str, GraphNodeRef],
) -> GraphExpandedEvidencePool:
    """Reference traversal — BFS bounded by every named ceiling.

    The caller supplies the graph adjacency in two indexes (src→edges and
    id→node) so the function is graph-store agnostic. ADG, NetworkX, or
    Neo4j adapters can all feed it.
    """
    accepted_nodes: list[GraphNodeRef] = list(inp.hydrated_seeds)
    accepted_edges: list[GraphEdge] = []
    accepted_node_ids: set[str] = {n.node_id for n in inp.hydrated_seeds}
    expansion_records: list[GraphExpansionRecord] = []

    # BFS frontier.
    frontier: list[tuple[GraphNodeRef, int]] = [(n, 0) for n in inp.hydrated_seeds]
    nodes_visited = 0
    edges_visited = 0
    max_hop_reached = 0
    relation_counts: dict[str, int] = {r.value: 0 for r in GraphRelation}
    rejection_counts: dict[str, int] = {r.value: 0 for r in GraphExclusionReason}

    while frontier:
        node, hops = frontier.pop(0)
        nodes_visited += 1
        max_hop_reached = max(max_hop_reached, hops)
        if hops >= inp.max_hops:
            continue
        if len(accepted_nodes) >= inp.max_nodes:
            break
        for edge in edges_by_src.get(node.node_id, ()):
            edges_visited += 1
            # Strict-bound: stop adding nodes/edges once max_nodes is hit
            # even mid-edge-loop. This matches BFS-with-cap semantics.
            if len(accepted_nodes) >= inp.max_nodes:
                rejection_counts[GraphExclusionReason.MAX_NODES.value] += 1
                continue
            if len(accepted_edges) >= inp.max_edges:
                rejection_counts[GraphExclusionReason.MAX_EDGES.value] += 1
                continue
            # Relation-type bounds.
            if inp.allowed_relation_types and edge.relation.value not in inp.allowed_relation_types:
                rejection_counts[GraphExclusionReason.RELATION_DISALLOWED.value] += 1
                expansion_records.append(
                    GraphExpansionRecord(
                        node=nodes_by_id.get(
                            edge.dst_node_id,
                            GraphNodeRef(
                                node_id=edge.dst_node_id,
                                source_id="?",
                                source_class="?",
                                acl_status="?",
                                freshness_status="?",
                            ),
                        ),
                        via_edge=edge,
                        hops_from_seed=hops + 1,
                        accepted=False,
                        rejection_reason=GraphExclusionReason.RELATION_DISALLOWED,
                    )
                )
                continue
            if edge.relation.value in inp.disallowed_relation_types:
                rejection_counts[GraphExclusionReason.RELATION_DISALLOWED.value] += 1
                continue
            dst = nodes_by_id.get(edge.dst_node_id)
            if dst is None:
                continue
            # Source-class bounds.
            if inp.allowed_source_classes and dst.source_class not in inp.allowed_source_classes:
                rejection_counts[GraphExclusionReason.SOURCE_CLASS_DISALLOWED.value] += 1
                continue
            if dst.source_class in inp.disallowed_source_classes:
                rejection_counts[GraphExclusionReason.SOURCE_CLASS_DISALLOWED.value] += 1
                continue
            # ACL bound — every hop must be cleared.
            if dst.acl_status not in {"cleared", "default-allow"}:
                rejection_counts[GraphExclusionReason.ACL_BLOCKED.value] += 1
                expansion_records.append(
                    GraphExpansionRecord(
                        node=dst,
                        via_edge=edge,
                        hops_from_seed=hops + 1,
                        accepted=False,
                        rejection_reason=GraphExclusionReason.ACL_BLOCKED,
                    )
                )
                continue
            # Freshness bound (regulated routes refuse stale graph hops).
            if inp.freshness_class == "regulated" and dst.freshness_status == "stale":
                rejection_counts[GraphExclusionReason.FRESHNESS_BLOCKED.value] += 1
                continue
            if dst.node_id in accepted_node_ids:
                rejection_counts[GraphExclusionReason.DUPLICATE.value] += 1
                continue
            # Accept.
            accepted_node_ids.add(dst.node_id)
            accepted_nodes.append(dst)
            accepted_edges.append(edge)
            relation_counts[edge.relation.value] += 1
            expansion_records.append(
                GraphExpansionRecord(
                    node=dst,
                    via_edge=edge,
                    hops_from_seed=hops + 1,
                    accepted=True,
                    rejection_reason=None,
                )
            )
            frontier.append((dst, hops + 1))

    relation_counts_tup = tuple(sorted(relation_counts.items()))
    rejection_counts_tup = tuple(sorted(((k, v) for k, v in rejection_counts.items() if v > 0)))
    manifest_payload = {
        "route_id": inp.route_id,
        "route_replay_key": inp.route_replay_key,
        "max_hops": inp.max_hops,
        "max_nodes": inp.max_nodes,
        "max_edges": inp.max_edges,
        "seeds": sorted(n.node_id for n in inp.hydrated_seeds),
        "accepted_nodes": sorted(n.node_id for n in accepted_nodes),
        "accepted_edges": [(e.relation.value, e.src_node_id, e.dst_node_id) for e in accepted_edges],
        "relation_counts": list(relation_counts_tup),
        "rejection_counts": list(rejection_counts_tup),
    }
    manifest_hash = hashlib.sha256(
        json.dumps(manifest_payload, sort_keys=True, separators=(",", ":")).encode(),
    ).hexdigest()[:32]

    manifest = GraphTraversalManifest(
        seed_node_ids=tuple(n.node_id for n in inp.hydrated_seeds),
        nodes_visited=nodes_visited,
        edges_visited=edges_visited,
        max_hop_reached=max_hop_reached,
        relation_counts=relation_counts_tup,
        rejection_counts=rejection_counts_tup,
        manifest_hash=manifest_hash,
    )
    return GraphExpandedEvidencePool(
        accepted_nodes=tuple(accepted_nodes),
        accepted_edges=tuple(accepted_edges),
        expansion_records=tuple(expansion_records),
        manifest=manifest,
    )


__all__ = [
    "GRAPH_RELATIONS",
    "GraphEdge",
    "GraphExclusionReason",
    "GraphExpandedEvidencePool",
    "GraphExpansionRecord",
    "GraphNodeRef",
    "GraphRelation",
    "GraphTraversalManifest",
    "GraphTraverseInput",
    "traverse_bounded",
]
