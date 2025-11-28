"""Observability - Runtime Layer

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

from __future__ import annotations

from runtime.observability.spans import *  # noqa: F401,F403
from runtime.observability.events import *  # noqa: F401,F403
from runtime.observability.emitters import *  # noqa: F401,F403
from runtime.observability.collectors import (  # noqa: F401
    get_events,
    clear_events as _clear_events_impl,
)


def get_all_events():
    """Backward-compatible alias for get_events()."""

    return get_events()


def clear_events() -> None:  # type: ignore[override]
    """Backward-compatible alias for collectors.clear_events()."""

    _clear_events_impl()




