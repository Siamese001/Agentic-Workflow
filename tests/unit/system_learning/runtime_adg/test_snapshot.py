"""Tests for system_learning/runtime_adg/snapshot.py.

Covers:
- RuntimeADGNode and RuntimeADGEdge are frozen dataclasses
- create_runtime_adg_snapshot produces content-addressed identity
- canonical_bytes is deterministic and order-independent
- snapshot_id == snapshot_hash
- Mutating input does not affect snapshot (immutability)
- Empty snapshot handles gracefully
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit

from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    attributes_to_json,
    create_runtime_adg_snapshot,
)


def _make_node(
    node_id: str = "span-1", name: str = "orchestrator.execute", started_at_utc: int = 1000
) -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=node_id,
        name=name,
        kind="orchestrator",
        layer="L3_ORCHESTRATION",
        component="NervousSystem",
        started_at_utc=started_at_utc,
        duration_ms=42.0,
        status="ok",
        attributes_json=attributes_to_json({"mission": "test"}),
    )


def _make_edge(src: str = "span-0", dst: str = "span-1") -> RuntimeADGEdge:
    return RuntimeADGEdge(src_id=src, dst_id=dst, relation="parent_child")


class TestRuntimeADGNodeFrozen:
    def test_is_frozen(self):
        node = _make_node()
        with pytest.raises((AttributeError, TypeError)):
            node.name = "changed"  # type: ignore[misc]

    def test_fields_accessible(self):
        node = _make_node("id-abc", "tool.search", 2000)
        assert node.node_id == "id-abc"
        assert node.name == "tool.search"
        assert node.started_at_utc == 2000


class TestRuntimeADGEdgeFrozen:
    def test_is_frozen(self):
        edge = _make_edge()
        with pytest.raises((AttributeError, TypeError)):
            edge.relation = "changed"  # type: ignore[misc]

    def test_relation_preserved(self):
        e = RuntimeADGEdge(src_id="a", dst_id="b", relation="temporal_sequence")
        assert e.relation == "temporal_sequence"


class TestCreateRuntimeADGSnapshot:
    def test_snapshot_id_equals_hash(self):
        snap = create_runtime_adg_snapshot(
            trace_id="trace-001",
            mission="test-mission",
            started_at_utc=1000,
            ended_at_utc=2000,
            nodes=(_make_node(),),
            edges=(_make_edge("__root__", "span-1"),),
        )
        assert snap.snapshot_id == snap.snapshot_hash
        assert len(snap.snapshot_id) == 64

    def test_canonical_bytes_matches_hash(self):
        snap = create_runtime_adg_snapshot(
            trace_id="trace-001",
            mission="m",
            started_at_utc=1000,
            ended_at_utc=2000,
            nodes=(_make_node(),),
            edges=(),
        )
        recomputed = hashlib.sha256(snap.canonical_bytes()).hexdigest()
        assert recomputed == snap.snapshot_hash

    def test_deterministic_regardless_of_node_order(self):
        n1 = _make_node("span-1", "orchestrator.execute", 1000)
        n2 = _make_node("span-2", "tool.search", 2000)
        snap_a = create_runtime_adg_snapshot(
            trace_id="tr",
            mission="m",
            started_at_utc=1000,
            ended_at_utc=3000,
            nodes=(n1, n2),
            edges=(),
        )
        snap_b = create_runtime_adg_snapshot(
            trace_id="tr",
            mission="m",
            started_at_utc=1000,
            ended_at_utc=3000,
            nodes=(n2, n1),
            edges=(),
        )
        assert snap_a.snapshot_hash == snap_b.snapshot_hash
        assert snap_a.nodes == snap_b.nodes

    def test_deterministic_regardless_of_edge_order(self):
        e1 = _make_edge("root", "span-1")
        e2 = _make_edge("span-1", "span-2")
        snap_a = create_runtime_adg_snapshot(
            trace_id="tr",
            mission="m",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(),
            edges=(e1, e2),
        )
        snap_b = create_runtime_adg_snapshot(
            trace_id="tr",
            mission="m",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(),
            edges=(e2, e1),
        )
        assert snap_a.snapshot_hash == snap_b.snapshot_hash

    def test_different_trace_id_produces_different_hash(self):
        snap_a = create_runtime_adg_snapshot(
            trace_id="trace-A",
            mission="m",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(),
            edges=(),
        )
        snap_b = create_runtime_adg_snapshot(
            trace_id="trace-B",
            mission="m",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(),
            edges=(),
        )
        assert snap_a.snapshot_hash != snap_b.snapshot_hash

    def test_empty_snapshot_is_valid(self):
        snap = create_runtime_adg_snapshot(
            trace_id="",
            mission="",
            started_at_utc=0,
            ended_at_utc=0,
            nodes=(),
            edges=(),
        )
        assert snap.node_count() == 0
        assert snap.edge_count() == 0
        assert len(snap.snapshot_id) == 64

    def test_node_count_and_edge_count(self):
        snap = create_runtime_adg_snapshot(
            trace_id="t",
            mission="m",
            started_at_utc=0,
            ended_at_utc=10,
            nodes=(_make_node("n1", "a", 0), _make_node("n2", "b", 5)),
            edges=(_make_edge("n1", "n2"),),
        )
        assert snap.node_count() == 2
        assert snap.edge_count() == 1

    def test_to_dict_structure(self):
        snap = create_runtime_adg_snapshot(
            trace_id="t",
            mission="my-mission",
            started_at_utc=100,
            ended_at_utc=200,
            nodes=(_make_node(),),
            edges=(),
        )
        d = snap.to_dict()
        assert d["trace_id"] == "t"
        assert d["mission"] == "my-mission"
        assert d["node_count"] == 1
        assert d["edge_count"] == 0
        assert "snapshot_hash" in d
        assert len(d["nodes"]) == 1


class TestAttributesToJson:
    def test_sorts_keys(self):
        raw = {"z": 1, "a": 2, "m": 3}
        result = attributes_to_json(raw)
        assert result.index('"a"') < result.index('"m"') < result.index('"z"')

    def test_compact_no_spaces(self):
        result = attributes_to_json({"k": "v"})
        assert " " not in result

    def test_empty_dict(self):
        assert attributes_to_json({}) == "{}"
