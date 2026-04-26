"""Phase 8 — OTEL trace tests."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    C0GraphSpan,
    NullSpanRecorder,
    run_graph_traverse,
)


def test_otel_trace_emits_seven_spans(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    span_names = {s.name for s in recorder.list_spans()}
    expected = {
        C0GraphSpan.ANCHOR_EXTRACT,
        C0GraphSpan.ANCHOR_RESOLVE,
        C0GraphSpan.PLAN,
        C0GraphSpan.TRAVERSE,
        C0GraphSpan.GATE,
        C0GraphSpan.CONTRADICTION_SCAN,
        C0GraphSpan.EMIT,
    }
    assert expected <= span_names


def test_otel_trace_proves_graphdb_path(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    pool = run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    traverse_spans = [s for s in recorder.list_spans() if s.name == C0GraphSpan.TRAVERSE]
    assert traverse_spans
    attrs = traverse_spans[0].attributes
    assert attrs["graph_source"] == pool.graph_traversal_manifest.graph_source
    # GraphDB-projection signal — must include projection_version.
    assert attrs["projection_version"]


def test_otel_trace_has_no_direct_sqlite_traversal(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    for s in recorder.list_spans():
        for v in s.attributes.values():
            if isinstance(v, str):
                assert "sqlite3" not in v.lower()
                assert "sqlite_canonical" not in v.lower()


def test_otel_emit_span_includes_manifest_hash(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    pool = run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    emit = next(s for s in recorder.list_spans() if s.name == C0GraphSpan.EMIT)
    assert emit.attributes["graph_manifest_hash"] == pool.graph_traversal_manifest.manifest_hash


def test_otel_gate_span_records_rejection_buckets(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    gate = next(s for s in recorder.list_spans() if s.name == C0GraphSpan.GATE)
    for attr in (
        "nodes_accepted",
        "nodes_rejected",
        "edges_accepted",
        "edges_rejected",
        "acl_rejections",
        "freshness_rejections",
        "relevance_rejections",
        "relation_rejections",
    ):
        assert attr in gate.attributes
