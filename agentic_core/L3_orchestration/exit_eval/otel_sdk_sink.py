"""Real OTel-SDK-backed ``SpanSink`` implementation.

Uses ``opentelemetry-api``/``opentelemetry-sdk`` when available, with a
graceful fallback to ``NoOpSpanSink`` when the SDK is not installed.
This keeps tests and minimal envs working without forcing OTel as a hard
dependency of ``exit_eval``.

Usage:

    from agentic_core.L3_orchestration.exit_eval.otel_sdk_sink import (
        build_span_sink,
    )

    sink = build_span_sink(service_name="exit_eval")
    pipeline = EvaluationPipeline(gates, bus_emitter, span_sink=sink)

When OTel is available, the sink:

- Records each gate as a span named ``exit_control.gate``, status
  ``OK`` / ``ERROR``, SpanKind ``INTERNAL``.
- Records per-dimension scores as span events (``dimension_scored``).
- Records dispositions as ``exit_control.disposition`` spans, linked to
  their parent gate spans via OTel span links.
- Returns SDK-format span-id strings so the pipeline can build cross-
  span linkage.

All OTel imports are scoped inside ``build_span_sink`` so importing this
module is always safe.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L3_orchestration.exit_eval.otel_spans import (
    DispositionSpan,
    GateSpan,
    NoOpSpanSink,
    SpanSink,
)

_LOG = logging.getLogger(__name__)


def _flatten_events(events: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    """OTel attributes must be primitive. Coerce for safety."""
    out: list[dict[str, Any]] = []
    for event in events:
        safe = {}
        for key, value in event.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[key] = value
            else:
                safe[key] = str(value)
        out.append(safe)
    return out


def _safe_attrs(attrs: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in attrs.items():
        if isinstance(value, (str, int, float, bool)):
            safe[key] = value
        elif value is None:
            # OTel treats None as missing; skip rather than emit.
            continue
        elif isinstance(value, (list, tuple)) and all(isinstance(v, (str, int, float, bool)) for v in value):
            safe[key] = list(value)
        else:
            safe[key] = str(value)
    return safe


class _OtelSpanSink:
    """``SpanSink`` implementation bound to a live OTel tracer.

    Instantiated only by ``build_span_sink``; direct construction keeps
    test code off the OTel import path entirely.
    """

    def __init__(self, tracer: Any, trace_module: Any) -> None:
        self._tracer = tracer
        self._trace = trace_module
        # Track last emitted span by id so the disposition sink can
        # build real OTel ``Link`` objects rather than opaque strings.
        self._spans_by_id: dict[str, Any] = {}

    def emit_gate(self, span: GateSpan) -> str:
        attrs = _safe_attrs(span.attributes)
        with self._tracer.start_as_current_span(
            span.name,
            kind=self._trace.SpanKind.INTERNAL,
            attributes=attrs,
        ) as otel_span:
            if span.status == "ERROR":
                otel_span.set_status(self._trace.Status(self._trace.StatusCode.ERROR))
            else:
                otel_span.set_status(self._trace.Status(self._trace.StatusCode.OK))
            for event in _flatten_events(span.events):
                name = str(event.pop("name", "dimension_scored"))
                otel_span.add_event(name, attributes=event)
            ctx = otel_span.get_span_context()
            span_id = f"{ctx.trace_id:032x}:{ctx.span_id:016x}"
            self._spans_by_id[span_id] = ctx
        return span_id

    def emit_disposition(self, span: DispositionSpan) -> str:
        attrs = _safe_attrs(span.attributes)
        # Build Link objects for each referenced gate span when we
        # captured its context; otherwise fall back to bare links.
        links = []
        for sid in span.gate_span_ids:
            ctx = self._spans_by_id.get(sid)
            if ctx is not None:
                links.append(self._trace.Link(ctx))
        with self._tracer.start_as_current_span(
            span.name,
            kind=self._trace.SpanKind.INTERNAL,
            attributes=attrs,
            links=links,
        ) as otel_span:
            if span.status == "ERROR":
                otel_span.set_status(self._trace.Status(self._trace.StatusCode.ERROR))
            else:
                otel_span.set_status(self._trace.Status(self._trace.StatusCode.OK))
            ctx = otel_span.get_span_context()
            return f"{ctx.trace_id:032x}:{ctx.span_id:016x}"


def build_span_sink(
    *,
    service_name: str = "exit_eval",
    tracer_name: str | None = None,
) -> SpanSink:
    """Return a live OTel-SDK sink, or a ``NoOpSpanSink`` if OTel is absent.

    Never raises. Logs a one-line debug message when falling back. This
    matters because ``exit_eval`` runs in contexts (tests, local dev,
    minimal images) where OTel is not wired and a hard import would
    turn every eval run into a crash.
    """
    try:
        from opentelemetry import trace  # type: ignore[import-not-found]
    except ImportError:
        _LOG.debug("OTel SDK unavailable; using NoOpSpanSink for %s", service_name)
        return NoOpSpanSink()

    try:
        tracer = trace.get_tracer(tracer_name or service_name)
    except (
        Exception
    ) as exc:  # guardian: allow-broad -- tracer provider init may raise provider-specific errors
        _LOG.warning("OTel get_tracer failed (%s); falling back to NoOp", exc)
        return NoOpSpanSink()

    return _OtelSpanSink(tracer=tracer, trace_module=trace)


__all__ = ["build_span_sink"]
