"""OTEL span helper for airlock boundary observability.

Per PROMPT_BOUNDARY_CONTRACT.md §6:
- pa.airlock_security_pass — emitted when an airlock processes content
- pa.injection_neutralization — emitted when content was neutralized
- pa.unsafe_payload_rejection — emitted when content was rejected

Optional dependency: opentelemetry. Falls back to no-op when unavailable.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator

try:
    from opentelemetry import trace as _otel_trace

    _tracer = _otel_trace.get_tracer("apps_rg.airlocks")
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    _tracer = None  # type: ignore[assignment]


@contextlib.contextmanager
def airlock_span(
    name: str,
    *,
    airlock: str,
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    **attributes: Any,
) -> Iterator[Any]:
    """Context manager for airlock OTEL spans.

    Args:
        name: Span name (e.g. "pa.airlock_security_pass", "pa.injection_neutralization")
        airlock: Airlock identifier (U0_USER_TEXT, C0_EVIDENCE, TOOL_OUTPUT, HITL_REENTRY)
        request_id: Request identifier
        run_id: Run identifier
        trace_id: Trace identifier
        **attributes: Additional span attributes

    Yields:
        OTEL span object (or None if OTEL unavailable).
    """
    if not OTEL_AVAILABLE or _tracer is None:
        yield None
        return

    with _tracer.start_as_current_span(name) as span:
        span.set_attribute("airlock", airlock)
        if request_id:
            span.set_attribute("request_id", request_id)
        if run_id:
            span.set_attribute("run_id", run_id)
        if trace_id:
            span.set_attribute("trace_id", trace_id)
        for key, value in attributes.items():
            span.set_attribute(key, str(value))
        yield span


def emit_airlock_event(
    span: Any,
    event_name: str,
    **attributes: Any,
) -> None:
    """Add an event to an active OTEL span.

    Args:
        span: Span returned from airlock_span (may be None if OTEL unavailable)
        event_name: Event name (e.g. "pa.injection_neutralized", "pa.payload_rejected")
        **attributes: Event attributes
    """
    if span is None or not OTEL_AVAILABLE:
        return

    string_attrs = {k: str(v) for k, v in attributes.items()}
    try:
        span.add_event(event_name, attributes=string_attrs)
    except (AttributeError, TypeError):  # guardian: allow-otel-optional -- span API drift
        pass


__all__ = ["OTEL_AVAILABLE", "airlock_span", "emit_airlock_event"]
