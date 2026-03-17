
from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("runtime_observability_collectors_util", "runtime_observability_collectors_util_digest")
record_execution_trace("runtime_observability_collectors_util", "runtime_observability_collectors_util_trace")

# from archives.legacy_root_folders.core.models.models import TelemetryEvent  # DEPRECATED: Archive import removed to protect archives from validation edits


_telemetry_buffer: list[TelemetryEvent] = []
_span_stack: list[dict[str, object]] = []


def append_event(evt: TelemetryEvent) -> None:
    """Append a telemetry event to the in-memory buffer."""

    _telemetry_buffer.append(evt)


def get_events() -> list[TelemetryEvent]:
    """Return a shallow copy of the telemetry buffer."""

    return list(_telemetry_buffer)


def clear_events() -> None:
    """Clear all telemetry events and open spans (primarily for tests)."""

    _telemetry_buffer.clear()
    _span_stack.clear()


def push_span(record: dict[str, object]) -> None:
    """Push a span record onto the span stack."""

    _span_stack.append(record)


def pop_span(record: dict[str, object]) -> None:
    """Remove a span record from the span stack if present."""

    if record in _span_stack:
        _span_stack.remove(record)


def span_stack() -> list[dict[str, object]]:
    """Return the internal span stack (for inspection-only)."""

    return _span_stack
