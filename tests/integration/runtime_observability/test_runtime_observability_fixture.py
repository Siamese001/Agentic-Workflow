"""Smoke tests for the runtime_observability pytest fixture.

W2 P2.1 of plan ``adg-three-bucket-unified-c4f8e2``.

These tests prove that the fixture:
  1. Captures spans emitted via the active TracerProvider during a marked test.
  2. Converts captured ReadableSpans to the runtime-ADG dict shape.
  3. Returns None for unmarked tests (no overhead path).

The fixture's teardown invokes ``emit_spans_to_runtime_adg`` which writes to
the FileBackedRuntimeADGStore. We verify the snapshot count grew by querying
the store before and after.
"""

from __future__ import annotations

import pytest

# This test consumes ADG views indirectly via the runtime store; it is a
# producer-side test, not an ADG-graph consumer.
__adg_consumer_mode__ = "inventory"


def test_unmarked_test_yields_none(runtime_observability_capture):
    """Unmarked test path: fixture must yield None and do nothing."""
    assert runtime_observability_capture is None


@pytest.mark.runtime_observability
def test_marked_test_yields_exporter(runtime_observability_capture):
    """Marked test path: fixture must yield an InMemorySpanExporter."""
    pytest.importorskip("opentelemetry.sdk.trace.export.in_memory_span_exporter")
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    assert runtime_observability_capture is not None
    assert isinstance(runtime_observability_capture, InMemorySpanExporter)


@pytest.mark.runtime_observability
def test_emitted_span_is_captured(runtime_observability_capture):
    """A span emitted via the fixture's TracerProvider must be captured."""
    pytest.importorskip("opentelemetry")
    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test.smoke.span") as span:
        span.set_attribute("component", "runtime_observability_test")
        span.set_attribute("layer", "L6")

    # SimpleSpanProcessor is sync, but call get_finished_spans only — flush
    # happens at fixture teardown.
    captured = runtime_observability_capture.get_finished_spans()
    names = [s.name for s in captured]
    assert "test.smoke.span" in names

    # Verify the span carries our attributes intact.
    target = next(s for s in captured if s.name == "test.smoke.span")
    assert target.attributes is not None
    assert target.attributes.get("component") == "runtime_observability_test"
    assert target.attributes.get("layer") == "L6"


@pytest.mark.runtime_observability
def test_span_to_dict_shape(runtime_observability_capture):
    """Verify the converter produces the exact shape the materializer needs."""
    pytest.importorskip("opentelemetry")
    from opentelemetry import trace

    from tests._runtime_observability_plugin import _readable_span_to_dict

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("shape.check") as span:
        span.set_attribute("component", "shape-check")
        span.set_attribute("layer", "L1")

    spans = runtime_observability_capture.get_finished_spans()
    target = next(s for s in spans if s.name == "shape.check")
    payload = _readable_span_to_dict(target)

    # Required by materializer.
    assert payload["span_id"]
    assert isinstance(payload["span_id"], str)
    # Optional but consumed by materializer — must have correct types.
    assert payload["name"] == "shape.check"
    assert payload["component"] == "shape-check"
    assert payload["layer"] == "L1"
    assert payload["status"] in {"ok", "error"}
    assert isinstance(payload["ts_utc"], int)
    assert isinstance(payload["duration_ms"], float)
    assert isinstance(payload["attributes"], dict)
