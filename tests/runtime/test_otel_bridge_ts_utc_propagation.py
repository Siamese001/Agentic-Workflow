"""Regression test: bridge MUST propagate ts_utc through to materializer.

Failure precedent (2026-04-30):
    Bridge emitted ``start_time_ns`` but the RuntimeADGMaterializer reads
    ``ts_utc``. Field-name mismatch silently zeroed every node's
    ``started_at_utc`` for weeks — visible only via the
    ``tools.otel.verify_apps_rg_traces`` reader after the apps_rg run.
    Snapshots were persisted but unfilterable by time, breaking the
    "no traces, no run" verification invariant.

Contract under test:
    1. Bridge.emit() produces span dicts containing ``ts_utc`` (ms-since-epoch).
    2. The ``ts_utc`` value is non-zero and approximately matches wall-clock.
    3. Materializer.materialize() copies ``ts_utc`` into
       RuntimeADGNode.started_at_utc and computes a non-zero
       snapshot.started_at_utc.
"""

from __future__ import annotations

import logging
import time

import pytest


def _make_record(name: str, msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=logging.DEBUG,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_bridge_emits_ts_utc_field() -> None:
    """Bridge must include ts_utc on every buffered span."""
    from agentic_core.runtime.contracts.otel_lifecycle_bridge import (
        AdgEmissionToOtelBridge,
    )

    bridge = AdgEmissionToOtelBridge(root_trace_id="test-trace-001")
    before_ms = int(time.time() * 1000)
    record = _make_record(
        "adg.records_execution_trace",
        "records_execution_trace root_trace_id=test layer=L0_routing op=test_op",
    )
    bridge.emit(record)
    after_ms = int(time.time() * 1000)

    spans = bridge.buffered_spans()
    assert len(spans) == 1, "bridge.emit produced no span"

    span = spans[0]
    assert "ts_utc" in span, (
        "span dict missing 'ts_utc' field — RuntimeADGMaterializer reads this "
        "field exclusively; without it every node's started_at_utc=0."
    )
    ts_utc = span["ts_utc"]
    assert isinstance(ts_utc, int), f"ts_utc must be int (ms-since-epoch), got {type(ts_utc)}"
    assert ts_utc > 0, "ts_utc must be non-zero (wall-clock at emit time)"
    # Allow 5s slack — record.created is set at LogRecord construction in
    # _make_record above, before the before_ms read.
    assert before_ms - 5_000 <= ts_utc <= after_ms + 5_000, (
        f"ts_utc={ts_utc} outside wall-clock window [{before_ms - 5_000}, {after_ms + 5_000}]; "
        "field is being computed from a stale source"
    )


def test_bridge_to_materializer_ts_propagation() -> None:
    """End-to-end: bridge → materializer → snapshot.started_at_utc must be > 0.

    This is the integration assertion that would have caught the 2026-04-30
    blackout. The bridge claims ``success=True ingested=N`` independently of
    timestamp correctness; only this field-level assertion catches the regression.
    """
    from agentic_core.runtime.contracts.otel_lifecycle_bridge import (
        AdgEmissionToOtelBridge,
    )
    from agentic_core.L6_system_learning.materializer import RuntimeADGMaterializer

    bridge = AdgEmissionToOtelBridge(root_trace_id="test-trace-002")
    bridge.emit(_make_record(
        "adg.records_execution_trace",
        "records_execution_trace root_trace_id=test layer=L0_routing op=test_a",
    ))
    bridge.emit(_make_record(
        "adg.pulls_context",
        "pulls_context root_trace_id=test source=test context=test_ctx",
    ))
    spans = bridge.buffered_spans()
    assert len(spans) == 2

    snapshot = RuntimeADGMaterializer().materialize(spans, mission="test_mission")

    assert snapshot.started_at_utc > 0, (
        f"snapshot.started_at_utc={snapshot.started_at_utc}; bridge→materializer "
        "field contract broken (probably missing 'ts_utc' in span dict)"
    )
    assert snapshot.ended_at_utc >= snapshot.started_at_utc
    assert len(snapshot.nodes) == 2
    for node in snapshot.nodes:
        assert node.started_at_utc > 0, (
            f"node.started_at_utc={node.started_at_utc} for span "
            f"{node.name}; materializer is reading ts_utc=0 — field name mismatch"
        )


def test_bridge_ts_utc_consistent_with_start_time_ns() -> None:
    """ts_utc (ms) and start_time_ns (ns) should refer to the same instant."""
    from agentic_core.runtime.contracts.otel_lifecycle_bridge import (
        AdgEmissionToOtelBridge,
    )

    bridge = AdgEmissionToOtelBridge(root_trace_id="test-trace-003")
    bridge.emit(_make_record(
        "adg.records_execution_trace",
        "records_execution_trace root_trace_id=test layer=L0 op=consistency_check",
    ))
    span = bridge.buffered_spans()[0]
    # ts_utc is ms; start_time_ns is ns; both derived from record.created.
    derived_ms_from_ns = span["start_time_ns"] // 1_000_000
    assert abs(derived_ms_from_ns - span["ts_utc"]) <= 1, (
        f"ts_utc={span['ts_utc']} disagrees with start_time_ns={span['start_time_ns']} "
        f"(derived ms={derived_ms_from_ns}); these must be the same instant."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
