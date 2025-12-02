"""
Schema definitions for orchestration-level schema access coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class AccessStrategy(Enum):
    """Orchestration access strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CACHED = "cached"
    STREAMING = "streaming"


class CoordinationScope(Enum):
    """Access coordination scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    MULTI_WORKFLOW = "multi_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class AccessCoordinationTask:
    """Schema for access coordination task."""
    task_id: str
    access_type: str
    target_schemas: List[str]
    access_strategy: AccessStrategy
    coordination_scope: CoordinationScope


@dataclass
class AccessCoordinationPlan:
    """Schema for access coordination plan."""
    plan_id: str
    strategy: AccessStrategy
    scope: CoordinationScope
    tasks: List[AccessCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class AccessCoordinationResult:
    """Schema for access coordination results."""
    coordination_id: str
    plan: AccessCoordinationPlan
    coordinated_access: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
