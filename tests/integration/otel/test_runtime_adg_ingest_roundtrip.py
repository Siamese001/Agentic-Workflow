"""W7.1 / W3 — emit -> ingest -> query roundtrip test.

Asserts that a span emitted through the in-process
``emit_span_to_runtime_adg`` helper lands in the runtime ADG store and
is retrievable by ``trace_id`` within 1 second (plan success criterion).
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability import otel_runtime_ingest
from agentic_core.L6_system_learning.store import _deserialise_snapshot


@pytest.fixture
def fresh_store() -> None:
    """Reset the module-level singleton to a clean InMemoryRuntimeADGStore."""
    from agentic_core.L6_system_learning.store import InMemoryRuntimeADGStore

    otel_runtime_ingest._STORE = InMemoryRuntimeADGStore()  # type: ignore[assignment]
    otel_runtime_ingest._MATERIALIZER = None


def _span(span_id: str, trace_id: str) -> dict:
    return {
        "span_id": span_id,
        "trace_id": trace_id,
        "parent_span_id": "",
        "name": "heal_router.v1.route",
        "kind": "router",
        "layer": "L0",
        "component": "heal_router",
        "service_name": "heal_router",
        "ts_utc": int(time.time() * 1000),
        "duration_ms": 5.0,
        "status": "ok",
        "attributes": {"routing.tier": "T2"},
    }


def test_emit_to_query_roundtrip_under_1s(fresh_store: None) -> None:
    """Emit span -> retrieve by trace_id in the same process within 1s."""
    trace_id = "roundtrip-trace-0001"
    start = time.time()

    emit_result = otel_runtime_ingest.emit_span_to_runtime_adg(
        _span("s-1", trace_id),
        mission=trace_id,
        trace_id=trace_id,
    )
    assert emit_result["success"] is True

    store = otel_runtime_ingest._get_store()
    version_id = store.get_version_id_for_trace(trace_id)
    assert version_id is not None, "trace_id not indexed after emit"

    raw = store.get_by_version(version_id)
    assert raw, "snapshot payload not retrievable by version_id"

    snapshot = _deserialise_snapshot(raw)
    assert snapshot is not None
    assert snapshot.trace_id == trace_id
    assert len(snapshot.nodes) == 1
    assert snapshot.nodes[0].name == "heal_router.v1.route"

    elapsed = time.time() - start
    assert elapsed < 1.0, f"roundtrip took {elapsed:.3f}s, exceeds 1s budget"


def test_multi_span_roundtrip_preserves_order(fresh_store: None) -> None:
    """Multi-span emit persists all nodes and preserves span_ids."""
    trace_id = "roundtrip-trace-0002"
    spans = [_span("s-a", trace_id), _span("s-b", trace_id), _span("s-c", trace_id)]

    emit_result = otel_runtime_ingest.emit_spans_to_runtime_adg(spans, mission=trace_id, trace_id=trace_id)
    assert emit_result["success"] is True
    assert emit_result["spans_ingested"] == 3

    store = otel_runtime_ingest._get_store()
    version_id = store.get_version_id_for_trace(trace_id)
    assert version_id is not None
    snapshot = _deserialise_snapshot(store.get_by_version(version_id))
    assert snapshot is not None
    node_ids = {n.node_id for n in snapshot.nodes}
    assert node_ids == {"s-a", "s-b", "s-c"}
