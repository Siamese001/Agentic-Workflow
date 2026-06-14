"""Regression — X1H observable-trace validator (Phase 6)."""

from __future__ import annotations

from agentic_core.runtime.exhaust.observable_trace_check import (
    check_observable_trace,
)


def _span(name, layer, kind, *, trace_id="trace-abc", span_id="s", parent=""):
    return {
        "name": name,
        "layer": layer,
        "kind": kind,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent,
        "status": "ok",
        "attributes": {},
    }


def _full_trace():
    return [
        _span("runtime.trace_root", "L0_routing", "trace_root", span_id="root"),
        _span("L2.step.seal", "L2_execution", "seal", span_id="l2", parent="root"),
        _span("exit.disposition", "L5_safety", "exit", span_id="exit", parent="l2"),
    ]


def test_full_trace_passes():
    result = check_observable_trace(_full_trace())
    assert result.status == "PASS"
    assert result.missing == ()
    assert result.span_count == 3
    assert result.trace_root == "trace-abc"


def test_empty_spans_fail():
    result = check_observable_trace([])
    assert result.status == "FAIL"
    assert "spans" in result.missing


def test_missing_exit_disposition_fails():
    spans = [
        _span("runtime.trace_root", "L0_routing", "trace_root", span_id="root"),
        _span("L2.step.seal", "L2_execution", "seal", span_id="l2", parent="root"),
    ]
    result = check_observable_trace(spans)
    assert result.status == "FAIL"
    assert "exit_disposition" in result.missing


def test_missing_l2_only_is_partial():
    spans = [
        _span("runtime.trace_root", "L0_routing", "trace_root", span_id="root"),
        _span("exit.disposition", "L5_safety", "exit", span_id="exit", parent="root"),
    ]
    result = check_observable_trace(spans)
    assert result.status == "PARTIAL"
    assert "l2_execution" in result.missing


def test_terminal_run_can_waive_l2_requirement():
    # An L0 R5 terminal never executes L2 — waiving the L2 requirement -> PASS.
    spans = [
        _span("runtime.trace_root", "L0_routing", "trace_root", span_id="root"),
        _span("exit.disposition", "L5_safety", "exit", span_id="exit", parent="root"),
    ]
    result = check_observable_trace(spans, require_l2_for_executed_run=False)
    assert result.status == "PASS"
