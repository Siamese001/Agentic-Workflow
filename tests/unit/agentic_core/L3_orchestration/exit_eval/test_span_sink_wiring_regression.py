"""Regression — Exit eval defaults to no-op; the tracing factory injects a sink.

Demonstrates the gap (direct ``EvaluationPipeline`` construction is silently
no-op) and the fix (``build_evaluation_pipeline_with_tracing`` bootstraps tracing
and injects ``build_span_sink()`` — a live OTel sink when OTel is present).
"""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval import (
    build_evaluation_pipeline_with_tracing,
)
from agentic_core.L3_orchestration.exit_eval.otel_sdk_sink import build_span_sink
from agentic_core.L3_orchestration.exit_eval.otel_spans import NoOpSpanSink
from agentic_core.L3_orchestration.exit_eval.pipeline import EvaluationPipeline


class _FakeGate:
    """Minimal stand-in — the pipeline only iterates gates inside ``run()``."""


class _FakeBus:
    def emit(self, row):  # pragma: no cover - never called (we don't run())
        return None


def test_direct_pipeline_defaults_to_noop_span_sink():
    pipe = EvaluationPipeline([_FakeGate()], bus_emitter=_FakeBus())
    assert isinstance(pipe._spans, NoOpSpanSink)


def test_factory_injects_build_span_sink_result():
    pipe = build_evaluation_pipeline_with_tracing([_FakeGate()], bus_emitter=_FakeBus())
    assert isinstance(pipe, EvaluationPipeline)
    # The factory injects exactly what build_span_sink() returns — never the
    # silent NoOp-by-default of the bare constructor.
    assert type(pipe._spans) is type(build_span_sink(service_name="exit_eval"))


def test_factory_sink_is_non_noop_when_otel_available():
    try:
        import opentelemetry  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip("OTel not installed; factory correctly falls back to NoOp")
    pipe = build_evaluation_pipeline_with_tracing([_FakeGate()], bus_emitter=_FakeBus())
    assert not isinstance(pipe._spans, NoOpSpanSink)
