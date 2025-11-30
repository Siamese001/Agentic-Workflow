# Observability system
from typing import List, Any, Optional

# Global event store for testing/stub purposes
_events: List[Any] = []

def record_event(event: Any) -> None:
    """Record an observability event"""
    _events.append(event)

def get_all_events() -> List[Any]:
    """Get all recorded events"""
    return _events.copy()

def clear_events() -> None:
    """Clear all recorded events"""
    _events.clear()
