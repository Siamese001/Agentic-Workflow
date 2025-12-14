"""Enum types for fetch_schema_history."""
import logging



logger = logging.getLogger(__name__)
class HistoryAction(Enum):
    """Types of history actions."""
    CREATED = 'created'
    UPDATED = 'updated'
    DEPRECATED = 'deprecated'
    ARCHIVED = 'archived'
    RESTORED = 'restored'
    CLONED = 'cloned'
