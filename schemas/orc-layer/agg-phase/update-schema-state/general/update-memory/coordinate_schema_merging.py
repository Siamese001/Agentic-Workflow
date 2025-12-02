"""
Schema definitions for orchestration-level schema merging coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class MergingStrategy(Enum):
    """Orchestration merging strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CONSENSUS_BASED = "consensus_based"
    HIERARCHICAL = "hierarchical"


class CoordinationLevel(Enum):
    """Merging coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class MergingCoordinationTask:
    """Schema for merging coordination task."""
    task_id: str
    merging_type: str
    target_schemas: List[str]
    merging_strategy: MergingStrategy
    coordination_level: CoordinationLevel


@dataclass
class MergingCoordinationPlan:
    """Schema for merging coordination plan."""
    plan_id: str
    strategy: MergingStrategy
    coordination_level: CoordinationLevel
    tasks: List[MergingCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class MergingCoordinationResult:
    """Schema for merging coordination results."""
    coordination_id: str
    plan: MergingCoordinationPlan
    coordinated_merges: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
