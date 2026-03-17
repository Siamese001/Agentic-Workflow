"""Observability clients utilities.

Provides tracing and monitoring functionality.
"""

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("observability_clients_util", "observability_clients_util_digest")
record_execution_trace("observability_clients_util", "observability_clients_util_trace")



def create_span(name: str, **kwargs) -> Any:
    """Create a tracing span.

    Args:
        name: Span name
        **kwargs: Additional attributes

    Returns:
        Span instance
    """
    return None


def record_exception(exception: Exception, **kwargs) -> None:
    """Record an exception in the tracing system.

    Args:
        exception: The exception to record
        **kwargs: Additional context
    """
    pass


def set_span_attribute(key: str, value: Any) -> None:
    """Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    pass
