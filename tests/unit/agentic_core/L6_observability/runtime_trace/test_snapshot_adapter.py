"""Tests for the runtime ADG snapshot -> validate_trace adapter.

Covers W1.2 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

import json

from agentic_core.L6_observability.runtime_trace import snapshot_to_spans
from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)


def _node(
    *,
    node_id: str,
    name: str,
    layer: str = "L0",
    component: str = "test",
    started_at_utc: int = 0,
    duration_ms: float = 1.0,
    status: str = "ok",
    attributes: dict | None = None,
    kind: str = "test",
) -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=node_id,
        name=name,
        kind=kind,
        layer=layer,
        component=component,
        started_at_utc=started_at_utc,
        duration_ms=duration_ms,
        status=status,
        attributes_json=json.dumps(attributes or {}, sort_keys=True),
    )


class TestSnapshotToSpans:
    def test_root_span_has_null_parent(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=10,
            nodes=(_node(node_id="a", name="root.span", started_at_utc=0),),
            edges=(RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),),
        )
        spans = snapshot_to_spans(snap)
        assert len(spans) == 1
        assert spans[0]["name"] == "root.span"
        assert spans[0]["parent_name"] is None

    def test_parent_resolved_by_name(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=10,
            nodes=(
                _node(node_id="a", name="parent.span", started_at_utc=0),
                _node(node_id="b", name="child.span", started_at_utc=1, layer="L1"),
            ),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="a", dst_id="b", relation="parent_child"),
            ),
        )
        spans = snapshot_to_spans(snap)
        by_name = {s["name"]: s for s in spans}
        assert by_name["parent.span"]["parent_name"] is None
        assert by_name["child.span"]["parent_name"] == "parent.span"

    def test_attributes_round_trip(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(
                _node(
                    node_id="a",
                    name="root",
                    attributes={"trace_id": "T1", "k": 5, "nested": {"x": 1}},
                ),
            ),
            edges=(RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),),
        )
        spans = snapshot_to_spans(snap)
        attrs = spans[0]["attributes"]
        assert attrs["trace_id"] == "T1"
        assert attrs["k"] == 5
        assert attrs["nested"] == {"x": 1}

    def test_write_edge_translated_to_writes_to(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(
                _node(node_id="a", name="src", started_at_utc=0),
                _node(node_id="b", name="dst", started_at_utc=1),
            ),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="__root__", dst_id="b", relation="parent_child"),
                # write_edge whose dst is a span_id - adapter resolves to span name.
                RuntimeADGEdge(src_id="a", dst_id="b", relation="write_edge"),
            ),
        )
        spans = snapshot_to_spans(snap)
        src_span = next(s for s in spans if s["name"] == "src")
        assert {"to": "dst", "kind": "writes_to"} in src_span["edges"]

    def test_write_edge_with_literal_dst(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(_node(node_id="a", name="src"),),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                # write_edge dst is NOT a span_id - keep as literal string.
                RuntimeADGEdge(src_id="a", dst_id="external.kafka.topic", relation="write_edge"),
            ),
        )
        spans = snapshot_to_spans(snap)
        assert spans[0]["edges"] == [{"to": "external.kafka.topic", "kind": "writes_to"}]

    def test_dependency_translated_to_flows_to(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(
                _node(node_id="a", name="upstream", started_at_utc=0),
                _node(node_id="b", name="downstream", started_at_utc=1),
            ),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="__root__", dst_id="b", relation="parent_child"),
                RuntimeADGEdge(src_id="a", dst_id="b", relation="dependency"),
            ),
        )
        spans = snapshot_to_spans(snap)
        a = next(s for s in spans if s["name"] == "upstream")
        assert {"to": "downstream", "kind": "flows_to"} in a["edges"]

    def test_temporal_sequence_dropped(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(
                _node(node_id="a", name="first", started_at_utc=0),
                _node(node_id="b", name="second", started_at_utc=1),
            ),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="__root__", dst_id="b", relation="parent_child"),
                RuntimeADGEdge(src_id="a", dst_id="b", relation="temporal_sequence"),
            ),
        )
        spans = snapshot_to_spans(snap)
        for s in spans:
            assert all(e.get("kind") != "temporal_sequence" for e in s["edges"])

    def test_unknown_edge_kind_passed_through(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(_node(node_id="a", name="src"),),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="a", dst_id="other-target", relation="custom_relation"),
            ),
        )
        spans = snapshot_to_spans(snap)
        assert spans[0]["edges"] == [{"to": "other-target", "kind": "custom_relation"}]

    def test_status_carries_through(self) -> None:
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(
                _node(node_id="a", name="ok.span", status="ok"),
                _node(node_id="b", name="err.span", status="error", started_at_utc=1),
            ),
            edges=(
                RuntimeADGEdge(src_id="__root__", dst_id="a", relation="parent_child"),
                RuntimeADGEdge(src_id="__root__", dst_id="b", relation="parent_child"),
            ),
        )
        spans = snapshot_to_spans(snap)
        by_name = {s["name"]: s for s in spans}
        assert by_name["ok.span"]["status"] == "ok"
        assert by_name["err.span"]["status"] == "error"

    def test_malformed_attributes_json_yields_empty_dict(self) -> None:
        # Construct a node directly with an invalid attributes_json — the
        # adapter must not raise; it falls back to an empty dict.
        bad = RuntimeADGNode(
            node_id="x",
            name="bad",
            kind="test",
            layer="L0",
            component="test",
            started_at_utc=0,
            duration_ms=1.0,
            status="ok",
            attributes_json="not-valid-json",
        )
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m1",
            started_at_utc=0,
            ended_at_utc=1,
            nodes=(bad,),
            edges=(RuntimeADGEdge(src_id="__root__", dst_id="x", relation="parent_child"),),
        )
        spans = snapshot_to_spans(snap)
        assert spans[0]["attributes"] == {}
