from __future__ import annotations

from typing import Any, Dict, List

from core.models.models import TelemetryEvent


_telemetry_buffer: List[TelemetryEvent] = []
_span_stack: List[Dict[str, Any]] = []


def append_event(evt: TelemetryEvent) -> None:
    """Append a telemetry event to the in-memory buffer."""

    _telemetry_buffer.append(evt)


def get_events() -> List[TelemetryEvent]:
    """Return a shallow copy of the telemetry buffer."""

    return list(_telemetry_buffer)


def clear_events() -> None:
    """Clear all telemetry events and open spans (primarily for tests)."""

    _telemetry_buffer.clear()
    _span_stack.clear()


def push_span(record: Dict[str, Any]) -> None:
    """Push a span record onto the span stack."""

    _span_stack.append(record)


def pop_span(record: Dict[str, Any]) -> None:
    """Remove a span record from the span stack if present."""

    if record in _span_stack:
        _span_stack.remove(record)


def span_stack() -> List[Dict[str, Any]]:
    """Return the internal span stack (for inspection-only)."""

    return _span_stack



