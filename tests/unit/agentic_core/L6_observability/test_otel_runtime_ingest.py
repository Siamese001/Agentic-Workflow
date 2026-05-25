"""Shape tests for agentic_core.L6_observability.otel_runtime_ingest.

W7.1 / P1.1 success criteria: helper exposes ``emit_span_to_runtime_adg(span)``
and 3 shape tests pass.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from agentic_core.L6_observability import otel_runtime_ingest


def _fresh_store(_tmp_path: Path) -> None:
    """Swap the module-level singleton store for an in-memory one.

    InMemoryRuntimeADGStore shares the same persist() interface and is
    L4-compliance-free, which is appropriate for shape tests that do not
    exercise file-backed persistence. File-backed ingest is covered by the
    W3 round-trip integration test.
    """
    from agentic_core.L6_system_learning.runtime_adg.store import InMemoryRuntimeADGStore

    otel_runtime_ingest._STORE = InMemoryRuntimeADGStore()  # type: ignore[assignment]
    otel_runtime_ingest._MATERIALIZER = None


def _sample_span(span_id: str = "s-001", trace_id: str = "t-001") -> dict:
    base_ts = int(time.time() * 1000)
    return {
        "span_id": span_id,
        "trace_id": trace_id,
        "parent_span_id": "",
        "name": "heal_router.decide",
        "kind": "orchestrator",
        "layer": "L3",
        "component": "heal_router",
        "service_name": "heal_router",
        "ts_utc": base_ts,
        "duration_ms": 12.5,
        "status": "ok",
        "attributes": {"decision": "route_a"},
    }


def test_emit_span_to_runtime_adg_happy_path(tmp_path: Path) -> None:
    """Single-span emit returns success=True with snapshot_id + version_id."""
    _fresh_store(tmp_path)
    result = otel_runtime_ingest.emit_span_to_runtime_adg(
        _sample_span(),
        trace_id="t-001",
        mission="shape-test-1",
    )
    assert result["success"] is True
    assert result["spans_ingested"] == 1
    assert isinstance(result["snapshot_id"], str) and result["snapshot_id"]
    assert isinstance(result["version_id"], str) and result["version_id"]
    assert result["trace_id"] == "t-001"
    assert result["mission"] == "shape-test-1"


def test_emit_spans_to_runtime_adg_rejects_empty(tmp_path: Path) -> None:
    """Empty list is rejected without raising; returns success=False."""
    _fresh_store(tmp_path)
    result = otel_runtime_ingest.emit_spans_to_runtime_adg([], trace_id="t-002")
    assert result["success"] is False
    assert result["spans_ingested"] == 0
    assert "non-empty" in result["error"].lower()


def test_emit_spans_idempotent_same_snapshot_id(tmp_path: Path) -> None:
    """Idempotency: emitting identical spans twice yields the same snapshot_id.

    FileBackedRuntimeADGStore is content-addressable, so the same input
    materializes to the same snapshot_id (SHA-256 of canonical_bytes()).
    """
    _fresh_store(tmp_path)
    spans = [_sample_span("s-a", "t-003"), _sample_span("s-b", "t-003")]
    # Pin mission so canonical bytes are stable across calls
    r1 = otel_runtime_ingest.emit_spans_to_runtime_adg(spans, mission="idempotent-test", trace_id="t-003")
    r2 = otel_runtime_ingest.emit_spans_to_runtime_adg(spans, mission="idempotent-test", trace_id="t-003")
    assert r1["success"] is True and r2["success"] is True
    assert r1["snapshot_id"] == r2["snapshot_id"]
    assert r1["version_id"] == r2["version_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
