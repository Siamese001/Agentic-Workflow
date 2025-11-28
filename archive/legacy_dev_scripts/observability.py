"""
Provides observability compatibility shim for resume generation system.

Ensures runtime monitoring and tracking capabilities for improved
resume generation quality and debugging.
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
    """Retrieves all observability events for resume generation monitoring.

    Ensures comprehensive tracking of resume generation processes
    for quality assurance and debugging.
    """
    return get_events()


def clear_events() -> None:  # type: ignore[override]
    """Clears observability events to maintain clean monitoring state.

    Ensures resume generation tracking remains organized and
    manageable for quality control purposes.
    """
    _clear_events_impl()




