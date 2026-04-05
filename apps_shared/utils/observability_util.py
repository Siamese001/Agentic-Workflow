
from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("observability_util", "observability_util_digest")
record_execution_trace("observability_util", "observability_util_trace")

"""observability - Runtime Layer

This module provides observability compatibility shim.

Layer: Runtime/Infrastructure
Responsibilities:
- Forward to runtime.observability
- Maintain backward compatibility
- Provide unified observability API

Non-responsibilities:
- Business logic
- Layer-specific operations
"""

# FILE: observability.py

_events: list[dict] = []


def get_events() -> list[dict]:
    """Get all recorded events."""
    return _events.copy()


def _clear_events_impl() -> None:
    """Clear all recorded events."""
    _events.clear()


def get_all_events() -> list:
    """Backward-compatible alias for get_events()."""

    return get_events()


def clear_events() -> None:  # type: ignore[override]
    """Backward-compatible alias for collectors.clear_events()."""

    _clear_events_impl()
