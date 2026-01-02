from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''

from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
EVENTS: List[Dict[str, object]] = []


def append_event(event: Dict[str, object]) -> None:
    """Append a raw event object to the in-memory agentic event buffer."""

    EVENTS.append(event)


def get_events() -> List[Dict[str, object]]:
    """Return a snapshot of all collected agentic events."""

    return list(EVENTS)


def clear_events() -> None:
    """Clear all collected agentic events."""

    EVENTS.clear()
