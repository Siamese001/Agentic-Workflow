"""
Runtime observability module stub.

Placeholder implementation to fix import violations.
"""

from typing import Any, Dict, Optional


def record_event(event_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Record an event for observability."""
    pass


def record_exception(error_name: str, exception: Exception) -> None:
    """Record an exception for observability."""
    pass


__all__ = ["record_event", "record_exception"]
