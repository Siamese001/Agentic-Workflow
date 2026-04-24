"""Tests for ``otel_sdk_sink.build_span_sink``.

Covers the fallback path (no OTel installed) and the live path using
OTel's ``InMemorySpanExporter`` when available.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.otel_sdk_sink import (
    build_span_sink,
)
from agentic_core.L3_orchestration.exit_eval.otel_spans import (
    DispositionSpan,
    GateSpan,
    NoOpSpanSink,
)


def _sample_gate_span() -> GateSpan:
    return GateSpan(
        name="exit_control.gate",
        kind="INTERNAL",
        status="OK",
        attributes={
            "gate": "X1D",
            "run_id": "r1",
            "track": "regression",
            "trajectory_class": "demo",
            "rubric_version": "X1D@v1",
            "composition": "weighted",
            "passed": True,
            "abstain": False,
            "disposition_hint": "X3D",
            "reason_codes": [],
            "aggregate_score": 0.85,
            "aggregate_threshold": 0.75,
        },
        events=(
            {
                "name": "dimension_scored",
                "dim.name": "groundedness",
                "dim.score": 0.9,
                "dim.weight": 0.4,
                "dim.threshold": 0.8,
                "dim.passed": True,
                "dim.grader_class": "model_based",
                "dim.abstain": False,
                "dim.is_hard_gate": False,
            },
        ),
    )


def _sample_disposition_span(gate_id: str) -> DispositionSpan:
    return DispositionSpan(
        name="exit_control.disposition",
        kind="INTERNAL",
        status="OK",
        attributes={
            "disposition": "ALLOW",
            "run_id": "r1",
            "track": "regression",
            "trajectory_class": "demo",
            "reason_codes": [],
            "deny": False,
        },
        gate_span_ids=(gate_id,),
    )


class TestFallbackPath:
    def test_falls_back_to_noop_when_otel_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If ``opentelemetry`` can't be imported, return NoOpSpanSink."""
        import builtins

        real_import = builtins.__import__

        def fake_import(name: str, *args, **kwargs):
            if name == "opentelemetry" or name.startswith("opentelemetry."):
                raise ImportError(f"simulated: {name} unavailable")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        sink = build_span_sink(service_name="test-svc")
        assert isinstance(sink, NoOpSpanSink)
        # Still functional
        gate_id = sink.emit_gate(_sample_gate_span())
        disp_id = sink.emit_disposition(_sample_disposition_span(gate_id))
        assert gate_id and disp_id
        assert len(sink.gate_spans) == 1
        assert len(sink.disposition_spans) == 1


class TestLiveOtelPath:
    """Single consolidated test.

    OpenTelemetry's ``TracerProvider`` is a global singleton — it cannot
    be re-installed within the same process (the SDK explicitly refuses
    with 'Overriding of current TracerProvider is not allowed'). Under
    parallel test workers this made per-test fixtures unreliable, so
    every assertion runs here in one cohesive test.
    """

    def test_live_path_emits_gate_and_disposition_with_events_and_links(self) -> None:
        pytest.importorskip("opentelemetry.sdk.trace")
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )

        # Install provider only if the default no-op is still active; if a
        # real provider is already installed (from a previous test in the
        # same xdist worker), reuse its pipeline by attaching an exporter.
        current = trace.get_tracer_provider()
        exporter = InMemorySpanExporter()
        if isinstance(current, TracerProvider):
            current.add_span_processor(SimpleSpanProcessor(exporter))
        else:
            provider = TracerProvider()
            provider.add_span_processor(SimpleSpanProcessor(exporter))
            trace.set_tracer_provider(provider)

        sink = build_span_sink(service_name="exit_eval_test")
        gate_id = sink.emit_gate(_sample_gate_span())
        disp_id = sink.emit_disposition(_sample_disposition_span(gate_id))
        assert gate_id and disp_id

        spans = exporter.get_finished_spans()
        names = [s.name for s in spans]
        assert "exit_control.gate" in names
        assert "exit_control.disposition" in names

        # Per-dimension event
        gate_spans = [s for s in spans if s.name == "exit_control.gate"]
        assert any(
            any(e.name == "dimension_scored" for e in s.events)
            for s in gate_spans
        )

        # Disposition → Gate link
        disp_spans = [s for s in spans if s.name == "exit_control.disposition"]
        assert any(len(s.links) >= 1 for s in disp_spans)

        exporter.clear()
