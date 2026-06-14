"""Unit tests for agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``adapter`` (L0 C0.3 GraphRAG) defines the read-only ``GraphTraversalAdapter``
protocol, its frozen return dataclasses (GraphNeighbor / GraphRelationPath /
ProjectionManifest / GraphAdapterHealth), and the reference ``InMemoryGraphAdapter``.
Coverage targets the frozen-dataclass __post_init__ invariants and the pure,
deterministic in-memory adapter surface (resolve / neighbors / BFS path / manifest).
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
    AmbiguousAnchorResolution,
    GraphAdapterHealth,
    GraphNeighbor,
    GraphRelationPath,
    GraphTraversalAdapter,
    InMemoryGraphAdapter,
    ProjectionManifest,
    ResolvedGraphAnchor,
    UnresolvedAnchorResolution,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
    AnchorCandidate,
    AnchorType,
)


def _neighbor(**overrides: object) -> GraphNeighbor:
    base: dict[str, object] = {
        "node_id": "n1",
        "node_type": "document",
        "source_id": "s1",
        "source_type": "docs",
        "source_version": "v1",
        "relation_type": "references",
        "relation_path": ("references",),
        "hop_distance": 1,
        "tenant": None,
        "region": None,
        "data_class": None,
        "acl_status": "allowed",
        "freshness_status": "fresh",
        "confidence": 0.9,
        "lineage_refs": (),
        "span_ref": None,
        "graph_source": "InMemoryGraphDBProjection",
        "projection_version": "v1.0.0",
        "snapshot_pointer": "snap://memory#1",
        "payload_preview": None,
    }
    base.update(overrides)
    return GraphNeighbor(**base)  # type: ignore[arg-type]


class TestGraphNeighborInvariants:
    def test_defaults(self) -> None:
        n = _neighbor()
        assert n.is_projected is True
        assert n.authority_class is None

    def test_missing_node_id_raises(self) -> None:
        with pytest.raises(ValueError, match="node_id is required"):
            _neighbor(node_id="")

    def test_missing_relation_type_raises(self) -> None:
        with pytest.raises(ValueError, match="relation_type is required"):
            _neighbor(relation_type="")

    def test_negative_hop_distance_raises(self) -> None:
        with pytest.raises(ValueError, match="hop_distance must be >= 0"):
            _neighbor(hop_distance=-1)

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _neighbor().node_id = "other"  # type: ignore[misc]


class TestProjectionManifestAndHealth:
    def test_projection_manifest_defaults(self) -> None:
        m = ProjectionManifest(
            graph_source="g",
            projection_version="v1",
            snapshot_pointer="snap",
            snapshot_built_at="1970-01-01T00:00:00Z",
            canonical_source_hash="0" * 64,
        )
        assert m.is_stale is False
        assert m.stale_reason == ""

    def test_health_defaults(self) -> None:
        h = GraphAdapterHealth(healthy=True, backend="x", latency_p50_ms=0.1, latency_p95_ms=0.5)
        assert h.last_error == ""

    def test_relation_path_frozen(self) -> None:
        p = GraphRelationPath(start_node_id="a", end_node_id="b", relations=(), nodes=("a", "b"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.start_node_id = "c"  # type: ignore[misc]


class TestInMemoryAdapterProtocol:
    def test_satisfies_protocol(self) -> None:
        assert isinstance(InMemoryGraphAdapter(), GraphTraversalAdapter)

    def test_health_check(self) -> None:
        h = InMemoryGraphAdapter().health_check()
        assert h.healthy is True and h.backend == "in-memory"

    def test_projection_manifest_reflects_stale(self) -> None:
        adapter = InMemoryGraphAdapter()
        assert adapter.get_projection_manifest().is_stale is False
        adapter.mark_stale("snapshot moved")
        m = adapter.get_projection_manifest()
        assert m.is_stale is True and m.stale_reason == "snapshot moved"


class TestInMemoryAdapterNeighbors:
    def _two_node_adapter(self) -> InMemoryGraphAdapter:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        adapter.add_node("b")
        adapter.add_edge("a", "b", "references")
        return adapter

    def test_neighbors_returns_edge(self) -> None:
        adapter = self._two_node_adapter()
        out = adapter.get_neighbors("a", (), {}, limit=10)
        assert len(out) == 1 and out[0].node_id == "b"
        assert out[0].relation_type == "references"

    def test_neighbors_unknown_node_empty(self) -> None:
        assert self._two_node_adapter().get_neighbors("zzz", (), {}, limit=10) == ()

    def test_neighbors_relation_filter(self) -> None:
        adapter = self._two_node_adapter()
        assert adapter.get_neighbors("a", ("calls",), {}, limit=10) == ()
        assert len(adapter.get_neighbors("a", ("references",), {}, limit=10)) == 1

    def test_neighbors_respects_limit(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        for dst in ("b", "c", "d"):
            adapter.add_node(dst)
            adapter.add_edge("a", dst, "references")
        assert len(adapter.get_neighbors("a", (), {}, limit=2)) == 2

    def test_add_edge_missing_node_raises(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        with pytest.raises(KeyError, match="dst node not present"):
            adapter.add_edge("a", "missing", "references")


class TestInMemoryAdapterAnchorResolution:
    def test_exact_node_id_match(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        cand = AnchorCandidate(anchor_value="a", anchor_type=AnchorType.DOCUMENT, original_evidence_id="e1")
        res = adapter.resolve_anchor(cand, {})
        assert isinstance(res, ResolvedGraphAnchor)
        assert res.resolved_node_id == "a"
        assert res.resolution_reason == "exact_node_id_match"

    def test_unique_alias_match(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a", anchor_aliases=("alias-x",))
        cand = AnchorCandidate(anchor_value="alias-x", anchor_type=AnchorType.DOCUMENT, original_evidence_id="e1")
        res = adapter.resolve_anchor(cand, {})
        assert isinstance(res, ResolvedGraphAnchor)
        assert res.resolution_reason == "alias_unique_match"

    def test_ambiguous_alias(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a", anchor_aliases=("dup",))
        adapter.add_node("b", anchor_aliases=("dup",))
        cand = AnchorCandidate(anchor_value="dup", anchor_type=AnchorType.DOCUMENT, original_evidence_id="e1")
        res = adapter.resolve_anchor(cand, {})
        assert isinstance(res, AmbiguousAnchorResolution)
        assert len(res.candidates) == 2

    def test_unresolved(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        cand = AnchorCandidate(anchor_value="nope", anchor_type=AnchorType.DOCUMENT, original_evidence_id="e1")
        res = adapter.resolve_anchor(cand, {})
        assert isinstance(res, UnresolvedAnchorResolution)
        assert res.reason == "no_match"


class TestInMemoryAdapterRelationPath:
    def test_path_to_self_is_empty_relations(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        p = adapter.get_relation_path("a", "a")
        assert p.relations == () and p.nodes == ("a",)

    def test_bfs_shortest_path(self) -> None:
        adapter = InMemoryGraphAdapter()
        for nid in ("a", "b", "c"):
            adapter.add_node(nid)
        adapter.add_edge("a", "b", "r1")
        adapter.add_edge("b", "c", "r2")
        p = adapter.get_relation_path("a", "c")
        assert p.relations == ("r1", "r2")
        assert p.nodes == ("a", "b", "c")

    def test_no_path_returns_empty(self) -> None:
        adapter = InMemoryGraphAdapter()
        adapter.add_node("a")
        adapter.add_node("b")
        p = adapter.get_relation_path("a", "b")
        assert p.relations == () and p.nodes == ()
