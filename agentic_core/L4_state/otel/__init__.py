"""L4/UWG OTel helpers.

Re-exports the span emission helpers so callers can write::

    from agentic_core.L4_state.otel import emit_l4_span, emit_uwg_span
"""

from agentic_core.L4_state.otel.spans import (
    L4_READ_SPAN_NAMES,
    L4_REFRESH_SPAN_NAMES,
    SpanRecord,
    UWG_WRITE_SPAN_NAMES,
    emit_l4_span,
    emit_uwg_span,
    get_emitted_spans,
    reset_emitted_spans,
)

__all__ = [
    "SpanRecord",
    "emit_l4_span",
    "emit_uwg_span",
    "get_emitted_spans",
    "reset_emitted_spans",
    "L4_READ_SPAN_NAMES",
    "L4_REFRESH_SPAN_NAMES",
    "UWG_WRITE_SPAN_NAMES",
]
