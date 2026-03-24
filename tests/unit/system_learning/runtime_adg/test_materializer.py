"""Tests for system_learning/runtime_adg/materializer.py.

Covers:
- Empty span list produces valid empty snapshot
- Each span becomes exactly one node
- Parent-child edges are derived from parent_span_id
- Root spans get __root__ as src_id
- Temporal sequence edges are derived from ts_utc ordering
- Mission is inferred from root span attributes/name
- Trace ID falls back to first span's trace_id
- Explicit trace_id and mission override inference
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.runtime_adg.materializer import _ROOT_SENTINEL, RuntimeADGMaterializer
from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot


def _make_span(
    span_id: str,
    name: str,
    parent_span_id: str = "",
    trace_id: str = "tr-001",
    ts_utc: int = 1000,
    duration_ms: float = 10.0,
    kind: str = "orchestrator",
    layer: str = "L3_ORCHESTRATION",
    component: str = "TestComponent",
    status: str = "ok",
    attributes: dict | None = None,
) -> dict:
    return {
        "span_id": span_id,
        "name": name,
        "parent_span_id": parent_span_id,
        "trace_id": trace_id,
        "ts_utc": ts_utc,
        "duration_ms": duration_ms,
        "kind": kind,
        "layer": layer,
        "component": component,
        "status": status,
        "attributes": attributes or {},
    }


class TestMaterializeEmpty:
    def test_empty_spans_produces_valid_snapshot(self):
        mat = RuntimeADGMaterializer()
        snap = mat.materialize([])
        assert isinstance(snap, RuntimeADGSnapshot)
        assert snap.node_count() == 0
        assert snap.edge_count() == 0
        assert len(snap.snapshot_id) == 64

    def test_empty_with_explicit_trace_mission(self):
        mat = RuntimeADGMaterializer()
        snap = mat.materialize([], mission="explicit", trace_id="explicit-trace")
        assert snap.mission == "explicit"
        assert snap.trace_id == "explicit-trace"


class TestNodeExtraction:
    def test_each_span_becomes_one_node(self):
        spans = [
            _make_span("s1", "orchestrator.execute"),
            _make_span("s2", "tool.search", parent_span_id="s1"),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.node_count() == 2

    def test_node_fields_preserved(self):
        spans = [
            _make_span(
                "s1",
                "cognitive.think",
                kind="cognitive",
                layer="L1_COGNITION",
                component="CognitivePlane",
                ts_utc=5000,
                duration_ms=99.5,
                status="ok",
            )
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        node = snap.nodes[0]
        assert node.node_id == "s1"
        assert node.name == "cognitive.think"
        assert node.kind == "cognitive"
        assert node.layer == "L1_COGNITION"
        assert node.component == "CognitivePlane"
        assert node.started_at_utc == 5000
        assert node.duration_ms == 99.5
        assert node.status == "ok"

    def test_nodes_sorted_by_ts_utc(self):
        spans = [
            _make_span("s2", "second", ts_utc=2000),
            _make_span("s1", "first", ts_utc=1000),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.nodes[0].started_at_utc <= snap.nodes[1].started_at_utc


class TestParentChildEdges:
    def test_root_span_gets_root_sentinel(self):
        spans = [_make_span("root", "orchestrator.execute", parent_span_id="")]
        snap = RuntimeADGMaterializer().materialize(spans)
        pc_edges = [e for e in snap.edges if e.relation == "parent_child"]
        assert len(pc_edges) == 1
        assert pc_edges[0].src_id == _ROOT_SENTINEL
        assert pc_edges[0].dst_id == "root"

    def test_child_span_has_parent_as_src(self):
        spans = [
            _make_span("s1", "orchestrator.execute", parent_span_id=""),
            _make_span("s2", "tool.search", parent_span_id="s1"),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        pc_edges = {(e.src_id, e.dst_id): e for e in snap.edges if e.relation == "parent_child"}
        assert ("s1", "s2") in pc_edges
        assert (_ROOT_SENTINEL, "s1") in pc_edges

    def test_three_level_nesting(self):
        spans = [
            _make_span("s1", "orch", parent_span_id="", ts_utc=1000),
            _make_span("s2", "cog", parent_span_id="s1", ts_utc=1100),
            _make_span("s3", "tool", parent_span_id="s2", ts_utc=1200),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        pc_edges = {(e.src_id, e.dst_id) for e in snap.edges if e.relation == "parent_child"}
        assert (_ROOT_SENTINEL, "s1") in pc_edges
        assert ("s1", "s2") in pc_edges
        assert ("s2", "s3") in pc_edges


class TestTemporalEdges:
    def test_single_span_no_temporal_edges(self):
        spans = [_make_span("s1", "orch")]
        snap = RuntimeADGMaterializer().materialize(spans)
        temporal = [e for e in snap.edges if e.relation == "temporal_sequence"]
        assert temporal == []

    def test_two_spans_produce_one_temporal_edge(self):
        spans = [
            _make_span("s1", "first", ts_utc=1000),
            _make_span("s2", "second", ts_utc=2000),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        temporal = [e for e in snap.edges if e.relation == "temporal_sequence"]
        assert len(temporal) == 1
        assert temporal[0].src_id == "s1"
        assert temporal[0].dst_id == "s2"

    def test_temporal_edges_follow_ts_utc_order(self):
        spans = [
            _make_span("s3", "third", ts_utc=3000),
            _make_span("s1", "first", ts_utc=1000),
            _make_span("s2", "second", ts_utc=2000),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        temporal = sorted(
            [e for e in snap.edges if e.relation == "temporal_sequence"],
            key=lambda e: e.src_id,
        )
        assert temporal[0].src_id == "s1" and temporal[0].dst_id == "s2"
        assert temporal[1].src_id == "s2" and temporal[1].dst_id == "s3"


class TestMissionAndTraceInference:
    def test_trace_id_inferred_from_first_span(self):
        spans = [_make_span("s1", "orch", trace_id="inferred-trace")]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.trace_id == "inferred-trace"

    def test_explicit_trace_id_overrides_inference(self):
        spans = [_make_span("s1", "orch", trace_id="span-trace")]
        snap = RuntimeADGMaterializer().materialize(spans, trace_id="override-trace")
        assert snap.trace_id == "override-trace"

    def test_mission_inferred_from_root_span_attributes(self):
        spans = [
            _make_span(
                "s1", "orchestrator.execute", parent_span_id="", attributes={"mission": "campaign-run-007"}
            ),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.mission == "campaign-run-007"

    def test_mission_inferred_from_root_span_name_fallback(self):
        spans = [_make_span("s1", "orchestrator.execute", parent_span_id="")]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.mission == "orchestrator.execute"

    def test_explicit_mission_overrides_inference(self):
        spans = [
            _make_span(
                "s1", "orchestrator.execute", parent_span_id="", attributes={"mission": "inferred-mission"}
            ),
        ]
        snap = RuntimeADGMaterializer().materialize(spans, mission="override-mission")
        assert snap.mission == "override-mission"

    def test_trace_start_end_from_spans(self):
        spans = [
            _make_span("s1", "first", ts_utc=1000, duration_ms=50),
            _make_span("s2", "second", ts_utc=2000, duration_ms=100),
        ]
        snap = RuntimeADGMaterializer().materialize(spans)
        assert snap.started_at_utc == 1000
        assert snap.ended_at_utc == 2100


class TestMaterializerIdempotency:
    def test_same_spans_produce_same_hash(self):
        spans = [
            _make_span("s1", "orch", parent_span_id="", ts_utc=1000, duration_ms=200),
            _make_span("s2", "tool", parent_span_id="s1", ts_utc=1100, duration_ms=50),
        ]
        snap_a = RuntimeADGMaterializer().materialize(spans, mission="m", trace_id="t")
        snap_b = RuntimeADGMaterializer().materialize(spans, mission="m", trace_id="t")
        assert snap_a.snapshot_hash == snap_b.snapshot_hash
