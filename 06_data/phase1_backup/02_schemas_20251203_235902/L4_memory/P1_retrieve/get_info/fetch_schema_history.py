"""
Schema definitions for schema history fetching and retrieval.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class HistoryType(Enum):
    """Schema history types."""
    VERSION_HISTORY = "version_history"
    MODIFICATION_HISTORY = "modification_history"
    USAGE_HISTORY = "usage_history"
    VALIDATION_HISTORY = "validation_history"


class TimeRange(Enum):
    """History time ranges."""
    LAST_HOUR = "last_hour"
    LAST_DAY = "last_day"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    ALL_TIME = "all_time"


@dataclass
class HistoryQuery:
    """Schema for history query."""
    query_id: str
    history_type: HistoryType
    time_range: TimeRange
    target_schema_id: str
    query_parameters: Dict[str, Any]


@dataclass
class HistoryFetch:
    """Schema for history fetch operation."""
    fetch_id: str
    query: HistoryQuery
    fetch_timestamp: str
    fetch_strategy: str


@dataclass
class HistoryFetchResult:
    """Schema for history fetch results."""
    result_id: str
    fetch: HistoryFetch
    history_entries: List[Dict[str, Any]]
    fetch_successful: bool
    total_entries: int