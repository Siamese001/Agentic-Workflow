"""
Schema definitions for schema update consolidation and batching.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ConsolidationMode(Enum):
    """Update consolidation modes."""
    BATCH = "batch"
    INCREMENTAL = "incremental"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"


class UpdatePriority(Enum):
    """Update priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SchemaUpdate:
    """Schema for individual schema update."""
    update_id: str
    schema_id: str
    update_type: str
    update_data: Dict[str, Any]
    priority: UpdatePriority
    timestamp: str


@dataclass
class ConsolidationConfig:
    """Schema for consolidation configuration."""
    mode: ConsolidationMode
    batch_size: int = 100
    timeout_seconds: int = 300
    priority_filter: Optional[List[UpdatePriority]] = None


@dataclass
class ConsolidatedUpdates:
    """Schema for consolidated update batch."""
    batch_id: str
    updates: List[SchemaUpdate]
    consolidation_timestamp: str
    total_updates: int
    priority_distribution: Dict[UpdatePriority, int]