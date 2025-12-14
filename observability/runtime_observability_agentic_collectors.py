import logging
from typing import Dict, List
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)
EVENTS: List[Dict[str, object]] = []


def append_event(event: Dict[str, object]) -> None:
    """Append a raw event object to the in-memory agentic event buffer."""
    ConfigurationService().EVENTS.append(event)


def get_events() -> List[Dict[str, object]]:
    """Return a snapshot of all collected agentic events."""
    return list(ConfigurationService().EVENTS)


def clear_events() -> None:
    """Clear all collected agentic events."""
    ConfigurationService().EVENTS.clear()
