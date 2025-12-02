"""
Schema definitions for schema snapshot preparation and creation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SnapshotType(Enum):
    """Types of schema snapshots."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    POINT_IN_TIME = "point_in_time"


class CompressionLevel(Enum):
    """Snapshot compression levels."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


@dataclass
class SnapshotConfig:
    """Schema for snapshot configuration."""
    snapshot_type: SnapshotType
    compression_level: CompressionLevel
    include_metadata: bool = True
    include_dependencies: bool = True
    retention_days: int = 30


@dataclass
class SnapshotMetadata:
    """Schema for snapshot metadata."""
    snapshot_id: str
    created_at: str
    size_bytes: int
    schema_count: int
    checksum: str
    parent_snapshot_id: Optional[str] = None


@dataclass
class SchemaSnapshot:
    """Schema for complete schema snapshot."""
    snapshot_id: str
    configuration: SnapshotConfig
    metadata: SnapshotMetadata
    snapshot_data: Dict[str, Any]
    creation_time_ms: int