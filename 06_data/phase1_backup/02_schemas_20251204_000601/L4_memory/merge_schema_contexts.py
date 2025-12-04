"""
Schema definitions for schema context merging and integration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class MergeStrategy(Enum):
    """Context merging strategies."""
    UNION = "union"
    INTERSECTION = "intersection"
    PRIORITY_BASED = "priority_based"
    CUSTOM_LOGIC = "custom_logic"


class ConflictResolution(Enum):
    """Conflict resolution methods."""
    FIRST_WINS = "first_wins"
    LAST_WINS = "last_wins"
    MERGE_ALL = "merge_all"
    ESCALATE = "escalate"


@dataclass
class ContextMergeConfig:
    """Schema for context merge configuration."""
    merge_strategy: MergeStrategy
    conflict_resolution: ConflictResolution
    priority_order: Optional[List[str]] = None
    preserve_sources: bool = True


@dataclass
class MergeConflict:
    """Schema for merge conflict details."""
    conflict_id: str
    field_path: str
    source_values: Dict[str, Any]
    resolution_method: ConflictResolution
    resolved_value: Optional[Dict[str, Any]]


@dataclass
class MergedContext:
    """Schema for merged context result."""
    context_id: str
    source_contexts: List[str]
    merged_data: Dict[str, Any]
    conflicts: List[MergeConflict]
    merge_timestamp: str