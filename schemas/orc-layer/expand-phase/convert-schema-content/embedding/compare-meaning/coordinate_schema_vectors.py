"""
Schema definitions for orchestration-level schema vector coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class CoordinationStrategy(Enum):
    """Vector coordination strategies."""
    LOAD_BALANCED = "load_balanced"
    GEO_DISTRIBUTED = "geo_distributed"
    PRIORITY_BASED = "priority_based"
    RESOURCE_AWARE = "resource_aware"


class SynchronizationMode(Enum):
    """Vector synchronization modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    EVENT_DRIVEN = "event_driven"
    BATCH_SYNC = "batch_sync"


@dataclass
class VectorCoordinationTask:
    """Schema for vector coordination task."""
    task_id: str
    vector_set_id: str
    operation_type: str
    target_nodes: List[str]
    synchronization_requirements: Dict[str, Any]


@dataclass
class CoordinationPlan:
    """Schema for vector coordination plan."""
    plan_id: str
    strategy: CoordinationStrategy
    synchronization_mode: SynchronizationMode
    tasks: List[VectorCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class VectorCoordinationResult:
    """Schema for vector coordination results."""
    coordination_id: str
    plan: CoordinationPlan
    synchronized_vectors: List[str]
    failed_synchronizations: List[str]
    coordination_statistics: Dict[str, Any]
