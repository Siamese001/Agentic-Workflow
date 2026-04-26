"""C0.3 GRAPH TRAVERSE — bounded card-catalog walk.

Spec: C0 Context Engine.md lines 376-452. Pure-data; backend lives in
adapters. Traversal is intentionally a pure function from inputs +
adjacency-callback to outputs so it is deterministic, testable, and
replay-stable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping

from .hydration import HydratedChunk, HydratedEvidencePool
from .plan import GraphBounds
from .verdicts import GraphRelation


# Adjacency callback signature.
#
#   (node_id, allowed_relations) -> tuple of (relation, neighbor_id, neighbor_chunk)
#
# `neighbor_chunk` MUST already be hydrated; the traversal does not hydrate.
# Implementations MUST honor ACL/tenant/region/freshness — the traversal
# enforces bounds but cannot enforce ACL it does not see.
AdjacencyFn = Callable[
    [str, tuple[GraphRelation, ...]],
    tuple[tuple[GraphRelation, str, HydratedChunk], ...],
]


@dataclass(frozen=True)
class GraphHop:
    """One accepted hop along the traversal."""

    relation: GraphRelation
    src_chunk_id: str
    dst_chunk_id: str
    hop_depth: int
    accepted_reason: str

    def __post_init__(self) -> None:
        if self.hop_depth < 1:
            raise ValueError("hop_depth must be >= 1")
        if not self.accepted_reason.strip():
            raise ValueError("accepted_reason required")


@dataclass(frozen=True)
class GraphRejection:
    """One rejected expansion candidate (kept for audit/lineage)."""

    relation: GraphRelation
    src_chunk_id: str
    dst_chunk_id: str
    rejected_reason: str


@dataclass(frozen=True)
class GraphTraverseResult:
    """Spec lines 438-442 — output of C0.3."""

    plan_id: str
    hops: tuple[GraphHop, ...]
    rejections: tuple[GraphRejection, ...] = field(default_factory=tuple)
    relation_counts: Mapping[GraphRelation, int] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphExpandedEvidencePool:
    """The hydrated pool + the chunks discovered via graph traversal."""

    plan_id: str
    original: HydratedEvidencePool
    neighbors: tuple[HydratedChunk, ...]
    traverse: GraphTraverseResult

    @property
    def all_chunks(self) -> tuple[HydratedChunk, ...]:
        return tuple(self.original.hydrated) + self.neighbors


# Acceptance rules, spec lines 430-436.
def _accept_reason(
    relation: GraphRelation,
    src: HydratedChunk,
    dst: HydratedChunk,
) -> str | None:
    """Return acceptance reason or None to reject.

    Acceptance rules (spec):
      - directly clarifies candidate evidence
      - authoritative definition / version context
      - reveals contradiction or caveat
      - source lineage
    Rejection rules:
      - merely interesting but not support-relevant
      - ACL / tenant / region / freshness fails (caller must filter dst)
    """
    sm = src.candidate.manifest
    dm = dst.candidate.manifest
    if relation in (GraphRelation.DEFINES, GraphRelation.IMPLEMENTS):
        return "authoritative definition"
    if relation == GraphRelation.GOVERNED_BY:
        return "policy / version authority"
    if relation in (GraphRelation.CONTRADICTS, GraphRelation.SUPERSEDES):
        return "contradiction or supersession surfaces caveat"
    if relation == GraphRelation.OWNS:
        return "ownership / authority context"
    if relation in (GraphRelation.IMPORTS, GraphRelation.CALLS, GraphRelation.DEPENDS_ON):
        # accept if same source class / same canonical source family
        if src.candidate.source_class == dst.candidate.source_class:
            return "intra-source dependency clarification"
        return None
    if relation == GraphRelation.OBSERVED_IN:
        return "runtime / trace evidence"
    if relation == GraphRelation.REMEDIATED_BY:
        return "lineage to remediation context"
    if relation == GraphRelation.DERIVED_FROM:
        return "source lineage"
    if relation == GraphRelation.DUPLICATES:
        return None  # duplicates do not add support
    if relation == GraphRelation.REFERENCES:
        # accept if dst is in the same tenant/region as src
        if sm.tenant == dm.tenant and sm.region == dm.region:
            return "in-scope cross-reference"
        return None
    return None


def expand_graph(
    pool: HydratedEvidencePool,
    *,
    bounds: GraphBounds,
    adjacency: AdjacencyFn,
    allowed_relations: tuple[GraphRelation, ...] = (),
) -> GraphExpandedEvidencePool:
    """Bounded BFS traversal honoring max_hops and acceptance rules.

    `adjacency` is the read-only graph-store callback. The traversal:
      - never exceeds bounds.max_hops
      - never adds the same dst twice (dedupe by canonical_source_path + chunk_id)
      - never accepts relations outside `allowed_relations` if set
      - records every rejection for audit

    Hard NOs from spec lines 444-448:
      - No ACL escape through graph neighbors (caller's adjacency must filter)
      - No durable memory promotion
      - No unbounded graph walk
      - No self-routing into workflow
    """
    if bounds.max_hops <= 0 or not pool.hydrated:
        empty = GraphTraverseResult(plan_id=pool.plan_id, hops=())
        return GraphExpandedEvidencePool(
            plan_id=pool.plan_id, original=pool, neighbors=(), traverse=empty,
        )

    relations = allowed_relations or tuple(GraphRelation)
    seen_keys: set[tuple[str, str]] = set()
    for h in pool.hydrated:
        seen_keys.add((h.canonical_source_path, h.candidate.chunk_id))

    hops: list[GraphHop] = []
    rejections: list[GraphRejection] = []
    neighbors: list[HydratedChunk] = []
    relation_counts: dict[GraphRelation, int] = {}

    # frontier: list of (chunk, depth)
    frontier: list[tuple[HydratedChunk, int]] = [(h, 0) for h in pool.hydrated]
    while frontier:
        next_frontier: list[tuple[HydratedChunk, int]] = []
        for src, depth in frontier:
            if depth >= bounds.max_hops:
                continue
            edges = adjacency(src.candidate.chunk_id, relations)
            for relation, neighbor_id, neighbor_chunk in edges:
                key = (neighbor_chunk.canonical_source_path, neighbor_chunk.candidate.chunk_id)
                if key in seen_keys:
                    rejections.append(
                        GraphRejection(
                            relation=relation,
                            src_chunk_id=src.candidate.chunk_id,
                            dst_chunk_id=neighbor_id,
                            rejected_reason="duplicate of existing chunk",
                        )
                    )
                    continue
                reason = _accept_reason(relation, src, neighbor_chunk)
                if reason is None:
                    rejections.append(
                        GraphRejection(
                            relation=relation,
                            src_chunk_id=src.candidate.chunk_id,
                            dst_chunk_id=neighbor_id,
                            rejected_reason="not support-relevant for relation type",
                        )
                    )
                    continue
                seen_keys.add(key)
                neighbors.append(neighbor_chunk)
                hops.append(
                    GraphHop(
                        relation=relation,
                        src_chunk_id=src.candidate.chunk_id,
                        dst_chunk_id=neighbor_id,
                        hop_depth=depth + 1,
                        accepted_reason=reason,
                    )
                )
                relation_counts[relation] = relation_counts.get(relation, 0) + 1
                next_frontier.append((neighbor_chunk, depth + 1))
        frontier = next_frontier

    traverse = GraphTraverseResult(
        plan_id=pool.plan_id,
        hops=tuple(hops),
        rejections=tuple(rejections),
        relation_counts=dict(relation_counts),
    )
    return GraphExpandedEvidencePool(
        plan_id=pool.plan_id,
        original=pool,
        neighbors=tuple(neighbors),
        traverse=traverse,
    )


__all__ = [
    "AdjacencyFn",
    "GraphExpandedEvidencePool",
    "GraphHop",
    "GraphRejection",
    "GraphTraverseResult",
    "expand_graph",
]
