"""
Schema definitions for schema history fetching and temporal queries.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class HistoryType(Enum):
    """Types of schema history."""
    VERSION_HISTORY = "version_history"
    MODIFICATION_HISTORY = "modification_history"
    USAGE_HISTORY = "usage_history"
    DEPENDENCY_HISTORY = "dependency_history"


class TimeRange(Enum):
    """Time range types for history queries."""
    ALL_TIME = "all_time"
    LAST_24_HOURS = "last_24_hours"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    CUSTOM_RANGE = "custom_range"


@dataclass
class HistoryQuery:
    """Schema for history retrieval query."""
    query_id: str
    schema_id: str
    history_type: HistoryType
    time_range: TimeRange
    custom_start_date: Optional[str] = None
    custom_end_date: Optional[str] = None


@dataclass
class HistoryEntry:
    """Schema for individual history entry."""
    entry_id: str
    timestamp: str
    change_type: str
    description: str
    changed_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SchemaHistory:
    """Schema for complete schema history."""
    history_id: str
    schema_id: str
    entries: List[HistoryEntry]
    total_entries: int
    query_metadata: Dict[str, Any]