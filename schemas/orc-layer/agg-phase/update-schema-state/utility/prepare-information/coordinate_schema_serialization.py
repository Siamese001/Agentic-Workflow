"""
Schema definitions for orchestration-level schema serialization coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SerializationStrategy(Enum):
    """Orchestration serialization strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    BATCH_PROCESSED = "batch_processed"
    STREAMING = "streaming"


class CoordinationLevel(Enum):
    """Serialization coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class SerializationCoordinationTask:
    """Schema for serialization coordination task."""
    task_id: str
    serialization_type: str
    target_schemas: List[str]
    serialization_strategy: SerializationStrategy
    coordination_level: CoordinationLevel


@dataclass
class SerializationCoordinationPlan:
    """Schema for serialization coordination plan."""
    plan_id: str
    strategy: SerializationStrategy
    coordination_level: CoordinationLevel
    tasks: List[SerializationCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class SerializationCoordinationResult:
    """Schema for serialization coordination results."""
    coordination_id: str
    plan: SerializationCoordinationPlan
    coordinated_serializations: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
