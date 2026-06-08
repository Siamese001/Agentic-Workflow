"""Regression tests for the L2 emitter tracer-cache ordering bug.

Before the generic provider bootstrap existed, ``l2_otel_emitter._resolve_tracer``
could cache OpenTelemetry's default ``ProxyTracerProvider`` no-op tracer (when no
recording provider had been installed yet) and keep it for the whole process —
dropping every L2 span even after a provider was later installed. The bootstrap
now calls :func:`reset_l2_tracer_cache` post-install to clear that stranded cache.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.observability import l2_otel_emitter as l2
from agentic_core.tracing import provider_bootstrap as pb


@pytest.fixture(autouse=True)
def _isolate_caches():
    saved_tracer, saved_avail = l2._TRACER, l2._OTEL_AVAILABLE
    pb._reset_for_tests()
    l2.reset_l2_tracer_cache()
    yield
    l2._TRACER, l2._OTEL_AVAILABLE = saved_tracer, saved_avail
    pb._reset_for_tests()


def test_reset_l2_tracer_cache_clears_globals():
    l2._TRACER = object()
    l2._OTEL_AVAILABLE = True
    l2.reset_l2_tracer_cache()
    assert l2._TRACER is None
    assert l2._OTEL_AVAILABLE is None


def test_bootstrap_resets_stranded_l2_cache(monkeypatch):
    from opentelemetry import trace

    # Simulate the bug precondition: emitter cached a non-recording proxy tracer.
    l2._TRACER = object()
    l2._OTEL_AVAILABLE = True

    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")
    status = pb.ensure_tracer_provider_from_env()
    assert status in ("console_installed", "provider_already_installed")

    # The bootstrap's post-install hook must have cleared the stranded cache.
    assert l2._TRACER is None

    # Next resolution binds to a real, recording tracer.
    tracer = l2._resolve_tracer()
    assert tracer is not None
    assert l2._OTEL_AVAILABLE is True
    span = tracer.start_span("probe")
    try:
        assert span.is_recording()
    finally:
        span.end()
    trace.get_tracer_provider().force_flush()


def test_resolve_tracer_still_noop_when_otel_marked_unavailable():
    # The constitutional fail-soft path must be preserved: when OTel is flagged
    # unavailable, resolution returns None without raising.
    l2._TRACER = None
    l2._OTEL_AVAILABLE = False
    assert l2._resolve_tracer() is None


def test_l2_span_exports_end_to_end_after_bootstrap(monkeypatch):
    """End-to-end export proof: bootstrap -> real L2SpanEmitter -> exporter captures the span.

    This is the gap the unit tests do not otherwise cover: a span emitted through
    the *real* production emitter actually reaches a SpanProcessor's exporter.
    Uses an in-memory exporter (same processor->exporter mechanism as OTLP) so the
    proof is deterministic and needs no collector.
    """
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    from agentic_core.L2_execution.observability.l2_otel_emitter import (
        L2SpanEmitter,
        build_required_attrs,
    )
    from agentic_core.L2_execution.observability.l2_spans import all_l2_span_names

    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "console")
    assert pb.ensure_tracer_provider_from_env() in (
        "console_installed",
        "provider_already_installed",
    )

    provider = trace.get_tracer_provider()
    assert isinstance(provider, TracerProvider)
    mem = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(mem))

    name = sorted(all_l2_span_names())[0]
    attrs = build_required_attrs(
        run_id="run-otel-proof",
        route_id="R4_SINGLE_ACTION",
        step_id="E1",
        blueprint_hash="bp",
        policy_hash="ph",
        replay_key="rk",
        capability_token="ct",
        sandbox_envelope_id="se",
        attempt_seed="as",
    )

    emitter = L2SpanEmitter()  # resolves the now-recording tracer post-bootstrap
    assert emitter.otel_available
    with emitter.span(name, attrs=attrs, validate=False):
        pass

    captured = [s.name for s in mem.get_finished_spans()]
    assert name in captured, f"expected exported span {name!r}; captured={captured}"
    # Drain the console batch processor now so it does not flush at interpreter
    # exit against pytest's closed capture file (benign-but-noisy otherwise).
    provider.force_flush()
