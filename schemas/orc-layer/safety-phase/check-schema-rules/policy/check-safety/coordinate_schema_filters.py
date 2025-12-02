"""
Schema definitions for orchestration-level schema filter coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class FilterStrategy(Enum):
    """Orchestration filter strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    RULE_BASED = "rule_based"
    ADAPTIVE = "adaptive"


class CoordinationLevel(Enum):
    """Filter coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class FilterCoordinationTask:
    """Schema for filter coordination task."""
    task_id: str
    filter_type: str
    target_schemas: List[str]
    filter_strategy: FilterStrategy
    coordination_level: CoordinationLevel


@dataclass
class FilterCoordinationPlan:
    """Schema for filter coordination plan."""
    plan_id: str
    strategy: FilterStrategy
    coordination_level: CoordinationLevel
    tasks: List[FilterCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class FilterCoordinationResult:
    """Schema for filter coordination results."""
    coordination_id: str
    plan: FilterCoordinationPlan
    coordinated_filters: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
