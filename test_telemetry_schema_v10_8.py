import importlib

import telemetry_schema


def test_metric_event_instantiation():
    tags = {"source": "unit-test", "env": "dev"}
    event = telemetry_schema.MetricEvent(name="requests", value=10.5, tags=tags)

    assert event.name == "requests"
    assert event.value == 10.5
    assert event.tags == tags


def test_span_event_fields():
    tags = {"operation": "fetch", "status": "ok"}
    span = telemetry_schema.SpanEvent(
        name="http_request",
        start_time_ms=1000,
        end_time_ms=1500,
        tags=tags,
    )

    assert span.name == "http_request"
    assert span.start_time_ms == 1000
    assert span.end_time_ms == 1500
    assert span.tags == tags


def test_trace_context_spans_deterministic():
    span = telemetry_schema.SpanEvent(
        name="child_span",
        start_time_ms=2000,
        end_time_ms=3000,
        tags={"detail": "child"},
    )
    spans = {"span-1": span}

    context = telemetry_schema.TraceContext(trace_id="trace-123", spans=spans)

    assert context.trace_id == "trace-123"
    assert context.spans == spans
    assert list(context.spans.keys()) == ["span-1"]


def test_module_has_no_side_effects():
    reloaded = importlib.reload(telemetry_schema)
    exported = {
        name
        for name in dir(reloaded)
        if not name.startswith("__")
    }
    expected = {"Any", "Dict", "MetricEvent", "SpanEvent", "TraceContext", "dataclass"}
    assert exported == expected
