
from typing import Dict, List
import logging


logger = logging.getLogger(__name__)
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
