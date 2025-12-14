"""Dataclass models for fetch_schema_history."""

from typing import Any, Dict, List, Optional
import logging

# from .fetch_schema_history_enums import *  # Star import removed

@dataclass
class SchemaChangeRecord:
    """Record of a schema change."""
    id: str
    schema_id: str
    action: HistoryAction
    timestamp: datetime
    version_from: Optional[str]
    version_to: Optional[str]
    changed_by: Optional[str]
    change_summary: Optional[str]
    changes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaHistoryQuery:
    """Query configuration for schema history."""
    schema_id: Optional[str] = None
    actions: List[HistoryAction] = field(default_factory=list)
    changed_by: Optional[str] = None
    version_from: Optional[str] = None
    version_to: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_changes: bool = True
    limit: int = 100
    offset: int = 0

@dataclass
class SchemaHistoryResult:
    """Result of schema history query."""
    records: List[SchemaChangeRecord]
    total_count: int
    query: SchemaHistoryQuery
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaEvolutionSummary:
    """Summary of schema evolution."""
    schema_id: str
    total_versions: int
    first_version: str
    latest_version: str
    creation_date: datetime
    last_modified: datetime
    modification_count: int
    contributors: List[str]
    major_changes: List[str] = field(default_factory=list)

@dataclass
class SchemaHistoryConfig:
    """Configuration for schema history management."""
    storage_path: str = 'data/schema_history'
    max_records_per_schema: int = 1000
    retention_days: int = 365
    enable_diff_tracking: bool = True
    backup_enabled: bool = True
