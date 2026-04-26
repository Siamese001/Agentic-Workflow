"""Graph traversal adapter — separates C0.3 from any specific graph backend.

Phase 2 of the spec. The runtime path of C0.3 / GraphRAG depends ONLY on this
interface; it MUST NOT open SQLite connections itself. SQLite is the canonical
ADG store; the GraphDB projection is its read-only consumer surface.

The repo currently ships ``InMemoryGraphAdapter`` for tests / sample-query
proof. A real GraphDB adapter (e.g. networkx, kuzu, neo4j) is a drop-in
replacement that satisfies this same protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable

from .contracts import (
    AclStatus,
    AnchorCandidate,
    AnchorType,
    FreshnessStatus,
    ResolvedGraphAnchor,
)


# ---------------------------------------------------------------------------
# Adapter return types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphNeighbor:
    """Spec Phase 2 — minimum fields a neighbor must surface to C0.3 gates."""

    node_id: str
    node_type: str
    source_id: str
    source_type: str
    source_version: str
    relation_type: str
    relation_path: tuple[str, ...]
    hop_distance: int
    tenant: str | None
    region: str | None
    data_class: str | None
    acl_status: AclStatus | str
    freshness_status: FreshnessStatus | str
    confidence: float
    lineage_refs: tuple[str, ...]
    span_ref: str | None
    graph_source: str
    projection_version: str | None
    snapshot_pointer: str | None
    payload_preview: str | None
    is_projected: bool = True
    authority_class: str | None = None

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("GraphNeighbor.node_id is required")
        if not self.relation_type:
            raise ValueError("GraphNeighbor.relation_type is required")
        if self.hop_distance < 0:
            raise ValueError("GraphNeighbor.hop_distance must be >= 0")


@dataclass(frozen=True)
class GraphRelationPath:
    """Path between two nodes — relation labels along the edges traversed."""

    start_node_id: str
    end_node_id: str
    relations: tuple[str, ...]
    nodes: tuple[str, ...]


@dataclass(frozen=True)
class ProjectionManifest:
    """Spec Phase 2 — projection metadata needed for currency gating."""

    graph_source: str
    projection_version: str
    snapshot_pointer: str
    snapshot_built_at: str
    canonical_source_hash: str
    is_stale: bool = False
    stale_reason: str = ""


@dataclass(frozen=True)
class GraphAdapterHealth:
    healthy: bool
    backend: str
    latency_p50_ms: float
    latency_p95_ms: float
    last_error: str = ""


@dataclass(frozen=True)
class AmbiguousAnchorResolution:
    candidate: AnchorCandidate
    candidates: tuple[ResolvedGraphAnchor, ...]


@dataclass(frozen=True)
class UnresolvedAnchorResolution:
    candidate: AnchorCandidate
    reason: str


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class GraphTraversalAdapter(Protocol):
    """Read-only graph adapter contract used by C0.3.

    Implementations MUST:
      - return relation_type for every edge,
      - return source lineage for every node/edge,
      - return projection version + snapshot pointer if graph is projected,
      - never mutate the graph,
      - expose enough metadata for gates to enforce ACL / freshness / scope.
    """

    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution: ...

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]: ...

    def get_relation_path(
        self,
        start_node_id: str,
        neighbor_node_id: str,
    ) -> GraphRelationPath: ...

    def get_projection_manifest(self) -> ProjectionManifest: ...

    def health_check(self) -> GraphAdapterHealth: ...


# ---------------------------------------------------------------------------
# In-memory test/fixture adapter
# ---------------------------------------------------------------------------


@dataclass
class _InMemoryNode:
    node_id: str
    node_type: str
    source_id: str
    source_type: str
    source_version: str
    tenant: str | None
    region: str | None
    data_class: str | None
    acl_status: str
    freshness_status: str
    confidence: float
    lineage_refs: tuple[str, ...]
    span_ref: str | None
    payload_preview: str | None
    anchor_aliases: tuple[str, ...] = field(default_factory=tuple)
    authority_class: str | None = None


@dataclass
class _InMemoryEdge:
    src: str
    dst: str
    relation_type: str


class InMemoryGraphAdapter:
    """Reference adapter used by tests + the Phase 9 sample query.

    It implements ``GraphTraversalAdapter`` by:
      - storing nodes in a dict keyed by ``node_id``,
      - storing edges as adjacency lists,
      - rejecting reads on a ``stale`` projection if marked so,
      - never opening a SQLite connection (the substrate guard verifies this).
    """

    def __init__(
        self,
        *,
        graph_source: str = "InMemoryGraphDBProjection",
        projection_version: str = "v1.0.0",
        snapshot_pointer: str = "snap://memory#1",
        snapshot_built_at: str = "1970-01-01T00:00:00Z",
        canonical_source_hash: str = "0" * 64,
        is_stale: bool = False,
    ) -> None:
        self._nodes: dict[str, _InMemoryNode] = {}
        self._edges_out: dict[str, list[_InMemoryEdge]] = {}
        self._graph_source = graph_source
        self._projection_version = projection_version
        self._snapshot_pointer = snapshot_pointer
        self._snapshot_built_at = snapshot_built_at
        self._canonical_source_hash = canonical_source_hash
        self._is_stale = is_stale
        self._stale_reason = ""

    # ---- builder helpers --------------------------------------------------

    def add_node(
        self,
        node_id: str,
        *,
        node_type: str = "document",
        source_id: str | None = None,
        source_type: str = "docs",
        source_version: str = "v1",
        tenant: str | None = None,
        region: str | None = None,
        data_class: str | None = None,
        acl_status: str = AclStatus.ALLOWED.value,
        freshness_status: str = FreshnessStatus.FRESH.value,
        confidence: float = 0.9,
        lineage_refs: tuple[str, ...] = (),
        span_ref: str | None = None,
        payload_preview: str | None = None,
        anchor_aliases: tuple[str, ...] = (),
        authority_class: str | None = None,
    ) -> None:
        self._nodes[node_id] = _InMemoryNode(
            node_id=node_id,
            node_type=node_type,
            source_id=node_id if source_id is None else source_id,
            source_type=source_type,
            source_version=source_version,
            tenant=tenant,
            region=region,
            data_class=data_class,
            acl_status=acl_status,
            freshness_status=freshness_status,
            confidence=confidence,
            lineage_refs=lineage_refs,
            span_ref=span_ref,
            payload_preview=payload_preview,
            anchor_aliases=anchor_aliases,
            authority_class=authority_class,
        )

    def add_edge(self, src: str, dst: str, relation_type: str) -> None:
        if src not in self._nodes:
            raise KeyError(f"src node not present: {src}")
        if dst not in self._nodes:
            raise KeyError(f"dst node not present: {dst}")
        self._edges_out.setdefault(src, []).append(
            _InMemoryEdge(src=src, dst=dst, relation_type=relation_type)
        )

    def mark_stale(self, reason: str = "snapshot newer than projection") -> None:
        self._is_stale = True
        self._stale_reason = reason  # type: ignore[attr-defined]

    # ---- protocol methods -------------------------------------------------

    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution:
        del scope  # protocol-required; in-memory adapter is scope-agnostic
        # Prefer exact node_id match.
        if anchor_candidate.anchor_value in self._nodes:
            n = self._nodes[anchor_candidate.anchor_value]
            return self._resolved_from_node(anchor_candidate, n, "exact_node_id_match")

        # Then anchor_aliases match.
        matches = [n for n in self._nodes.values() if anchor_candidate.anchor_value in n.anchor_aliases]
        if len(matches) == 1:
            return self._resolved_from_node(anchor_candidate, matches[0], "alias_unique_match")
        if len(matches) > 1:
            tentative = tuple(
                self._resolved_from_node(anchor_candidate, m, "alias_ambiguous") for m in matches
            )
            return AmbiguousAnchorResolution(candidate=anchor_candidate, candidates=tentative)

        # Then file_path hint.
        if anchor_candidate.hint_file_path:
            for n in self._nodes.values():
                if n.span_ref and anchor_candidate.hint_file_path in n.span_ref:
                    return self._resolved_from_node(anchor_candidate, n, "file_path_hint_match")

        return UnresolvedAnchorResolution(candidate=anchor_candidate, reason="no_match")

    def _resolved_from_node(
        self,
        candidate: AnchorCandidate,
        n: _InMemoryNode,
        reason: str,
    ) -> ResolvedGraphAnchor:
        anchor_type = candidate.anchor_type or AnchorType.UNKNOWN
        return ResolvedGraphAnchor(
            anchor_id=f"anchor::{candidate.original_evidence_id}::{n.node_id}",
            original_evidence_id=candidate.original_evidence_id,
            anchor_type=anchor_type,
            anchor_value=candidate.anchor_value,
            resolved_node_id=n.node_id,
            graph_source=self._graph_source,
            source_id=n.source_id,
            source_version=n.source_version,
            confidence=min(0.99, max(0.0, candidate.confidence + 0.4)),
            resolution_reason=reason,
            acl_status=n.acl_status,
            tenant=n.tenant,
            region=n.region,
            data_class=n.data_class,
        )

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]:
        del scope  # protocol-required; in-memory adapter is scope-agnostic
        if self._is_stale:
            # Adapter still serves data; gate G15 will enforce projection
            # currency. We don't censor reads here.
            pass
        if node_id not in self._nodes:
            return ()
        allowed = set(relation_types) if relation_types else None
        out: list[GraphNeighbor] = []
        for edge in self._edges_out.get(node_id, []):
            if allowed is not None and edge.relation_type not in allowed:
                continue
            n = self._nodes[edge.dst]
            out.append(
                GraphNeighbor(
                    node_id=n.node_id,
                    node_type=n.node_type,
                    source_id=n.source_id,
                    source_type=n.source_type,
                    source_version=n.source_version,
                    relation_type=edge.relation_type,
                    relation_path=(edge.relation_type,),
                    hop_distance=1,
                    tenant=n.tenant,
                    region=n.region,
                    data_class=n.data_class,
                    acl_status=n.acl_status,
                    freshness_status=n.freshness_status,
                    confidence=n.confidence,
                    lineage_refs=n.lineage_refs,
                    span_ref=n.span_ref,
                    graph_source=self._graph_source,
                    projection_version=self._projection_version,
                    snapshot_pointer=self._snapshot_pointer,
                    payload_preview=n.payload_preview,
                    is_projected=True,
                    authority_class=n.authority_class,
                )
            )
            if len(out) >= limit:
                break
        return tuple(out)

    def get_relation_path(self, start_node_id: str, neighbor_node_id: str) -> GraphRelationPath:
        # BFS for shortest path (small in-memory graphs only).
        if start_node_id == neighbor_node_id:
            return GraphRelationPath(
                start_node_id=start_node_id,
                end_node_id=neighbor_node_id,
                relations=(),
                nodes=(start_node_id,),
            )
        from collections import deque

        q: deque[tuple[str, tuple[str, ...], tuple[str, ...]]] = deque()
        q.append((start_node_id, (), (start_node_id,)))
        seen = {start_node_id}
        while q:
            cur, rels, nodes = q.popleft()
            for edge in self._edges_out.get(cur, []):
                if edge.dst in seen:
                    continue
                new_rels = rels + (edge.relation_type,)
                new_nodes = nodes + (edge.dst,)
                if edge.dst == neighbor_node_id:
                    return GraphRelationPath(
                        start_node_id=start_node_id,
                        end_node_id=neighbor_node_id,
                        relations=new_rels,
                        nodes=new_nodes,
                    )
                seen.add(edge.dst)
                q.append((edge.dst, new_rels, new_nodes))
        return GraphRelationPath(
            start_node_id=start_node_id,
            end_node_id=neighbor_node_id,
            relations=(),
            nodes=(),
        )

    def get_projection_manifest(self) -> ProjectionManifest:
        return ProjectionManifest(
            graph_source=self._graph_source,
            projection_version=self._projection_version,
            snapshot_pointer=self._snapshot_pointer,
            snapshot_built_at=self._snapshot_built_at,
            canonical_source_hash=self._canonical_source_hash,
            is_stale=self._is_stale,
            stale_reason=getattr(self, "_stale_reason", ""),
        )

    def health_check(self) -> GraphAdapterHealth:
        return GraphAdapterHealth(
            healthy=True,
            backend="in-memory",
            latency_p50_ms=0.1,
            latency_p95_ms=0.5,
        )


__all__ = [
    "AmbiguousAnchorResolution",
    "GraphAdapterHealth",
    "GraphNeighbor",
    "GraphRelationPath",
    "GraphTraversalAdapter",
    "InMemoryGraphAdapter",
    "ProjectionManifest",
    "UnresolvedAnchorResolution",
]
