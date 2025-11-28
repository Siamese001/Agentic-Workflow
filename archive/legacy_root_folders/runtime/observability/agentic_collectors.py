from __future__ import annotations

from typing import List, Any


EVENTS: List[Any] = []


def append_event(event: Any) -> None:
    """Append a raw event object to the in-memory agentic event buffer."""

    EVENTS.append(event)


def get_events() -> List[Any]:
    """Return a snapshot of all collected agentic events."""

    return list(EVENTS)


def clear_events() -> None:
    """Clear all collected agentic events."""

    EVENTS.clear()



