"""
Schema definitions for schema inspection logging and tracking.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class LogLevel(Enum):
    """Logging levels for inspection."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """Log entry categories."""
    INSPECTION_START = "inspection_start"
    INSPECTION_PROGRESS = "inspection_progress"
    INSPECTION_COMPLETE = "inspection_complete"
    FINDING_DISCOVERED = "finding_discovered"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class LogEntry:
    """Schema for individual log entry."""
    entry_id: str
    timestamp: str
    level: LogLevel
    category: LogCategory
    message: str
    schema_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class InspectionLog:
    """Schema for inspection log collection."""
    log_id: str
    inspection_id: str
    entries: List[LogEntry]
    start_time: str
    end_time: str
    total_entries: int


@dataclass
class LogConfiguration:
    """Schema for logging configuration."""
    min_level: LogLevel
    categories: List[LogCategory]
    include_metadata: bool = True
    max_entries_per_log: int = 10000