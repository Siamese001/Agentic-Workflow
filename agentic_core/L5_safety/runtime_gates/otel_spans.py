"""OTEL span emission for runtime gate evaluations.

Doctrine 00C.8 requires the following span names for every gate run:

- ``runtime_gate.mesh.start``
- ``runtime_gate.evaluate``
- ``runtime_gate.verdict``
- ``runtime_gate.mesh.complete``
- ``runtime_gate.bypass_detected``
- ``runtime_gate.unknown_material``
- ``runtime_gate.warn_material``
- ``runtime_gate.handoff_to_exit``

This module provides a thin emitter that prefers the OpenTelemetry SDK when
available and falls back to an in-process recorder otherwise. Tests use the
recorder to assert span coverage without needing the OTEL toolchain.
"""

from __future__ import annotations

# OTel GenAI semconv opt-out: this module emits OTel spans that are
# infrastructure / governance / state-write events, not GenAI agent /
# workflow / tool / model invocations. GenAI semconv attributes do
# not apply. Plan: three-bucket-gap-remediation-069806 (W3).
__non_genai_emitter__ = "L5 runtime safety gate spans — policy enforcement, not GenAI invocations"

import logging
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Optional OTEL import — guarded so this module works without the SDK.
try:  # pragma: no cover - import branch
    from opentelemetry import trace as _otel_trace

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _otel_trace = None  # type: ignore[assignment]
    _OTEL_AVAILABLE = False


SPAN_MESH_START = "runtime_gate.mesh.start"
SPAN_GATE_EVALUATE = "runtime_gate.evaluate"
SPAN_GATE_VERDICT = "runtime_gate.verdict"
SPAN_MESH_COMPLETE = "runtime_gate.mesh.complete"
SPAN_BYPASS_DETECTED = "runtime_gate.bypass_detected"
SPAN_UNKNOWN_MATERIAL = "runtime_gate.unknown_material"
SPAN_WARN_MATERIAL = "runtime_gate.warn_material"
SPAN_HANDOFF_TO_EXIT = "runtime_gate.handoff_to_exit"

ALL_SPAN_NAMES: tuple[str, ...] = (
    SPAN_MESH_START,
    SPAN_GATE_EVALUATE,
    SPAN_GATE_VERDICT,
    SPAN_MESH_COMPLETE,
    SPAN_BYPASS_DETECTED,
    SPAN_UNKNOWN_MATERIAL,
    SPAN_WARN_MATERIAL,
    SPAN_HANDOFF_TO_EXIT,
)


@dataclass
class RecordedSpan:
    """In-memory span record for tests / observability when OTEL is absent."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)


class _SpanRecorder:
    """Thread-safe in-process recorder for emitted runtime-gate spans.

    Tests can inspect ``recorder.spans`` to assert coverage (00C.8).
    """

    def __init__(self) -> None:
        self._spans: list[RecordedSpan] = []
        self._lock = threading.Lock()

    def record(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        with self._lock:
            self._spans.append(RecordedSpan(name=name, attributes=dict(attributes or {})))

    def reset(self) -> None:
        with self._lock:
            self._spans.clear()

    @property
    def spans(self) -> list[RecordedSpan]:
        with self._lock:
            return list(self._spans)

    def names(self) -> list[str]:
        with self._lock:
            return [s.name for s in self._spans]

    def by_name(self, name: str) -> list[RecordedSpan]:
        with self._lock:
            return [s for s in self._spans if s.name == name]


_RECORDER = _SpanRecorder()


def get_recorder() -> _SpanRecorder:
    """Return the process-wide span recorder (test surface)."""
    return _RECORDER


@contextmanager
def emit_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[None]:
    """Emit a runtime-gate OTEL span.

    Falls back to the in-process recorder when OTEL is unavailable. Always
    records to the recorder so tests can introspect emission regardless of
    whether the SDK is wired.
    """
    attrs = dict(attributes or {})
    _RECORDER.record(name, attrs)
    if _OTEL_AVAILABLE:
        try:  # pragma: no cover - exercised when SDK is installed
            tracer = _otel_trace.get_tracer("runtime_gates")
            with tracer.start_as_current_span(name, attributes=attrs):
                yield
                return
        except (RuntimeError, ValueError, TypeError) as exc:  # pragma: no cover
            logger.debug("runtime_gates otel emit failed: %s", exc)
    yield


def emit_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """Emit a one-shot span (no enclosed work)."""
    with emit_span(name, attributes):
        pass


__all__ = [
    "ALL_SPAN_NAMES",
    "SPAN_BYPASS_DETECTED",
    "SPAN_GATE_EVALUATE",
    "SPAN_GATE_VERDICT",
    "SPAN_HANDOFF_TO_EXIT",
    "SPAN_MESH_COMPLETE",
    "SPAN_MESH_START",
    "SPAN_UNKNOWN_MATERIAL",
    "SPAN_WARN_MATERIAL",
    "RecordedSpan",
    "emit_event",
    "emit_span",
    "get_recorder",
]
