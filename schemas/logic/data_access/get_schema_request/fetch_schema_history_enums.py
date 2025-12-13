"""Enum types for fetch_schema_history."""

from enum import Enum

class HistoryAction(Enum):
    """Types of history actions."""
    CREATED = 'created'
    UPDATED = 'updated'
    DEPRECATED = 'deprecated'
    ARCHIVED = 'archived'
    RESTORED = 'restored'
    CLONED = 'cloned'

