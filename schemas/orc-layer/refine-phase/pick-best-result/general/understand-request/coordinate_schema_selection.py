"""
Schema definitions for orchestration-level schema selection coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SelectionStrategy(Enum):
    """Schema selection strategies."""
    BEST_FIT = "best_fit"
    RANK_BASED = "rank_based"
    CONSTRAINT_DRIVEN = "constraint_driven"
    OPTIMIZATION_BASED = "optimization_based"


class CoordinationScope(Enum):
    """Selection coordination scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    MULTI_WORKFLOW = "multi_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class SelectionCoordinationTask:
    """Schema for selection coordination task."""
    task_id: str
    selection_criteria: Dict[str, Any]
    candidate_schemas: List[str]
    selection_strategy: SelectionStrategy
    coordination_scope: CoordinationScope


@dataclass
class SelectionCoordinationPlan:
    """Schema for selection coordination plan."""
    plan_id: str
    strategy: SelectionStrategy
    scope: CoordinationScope
    tasks: List[SelectionCoordinationTask]
    resource_requirements: Dict[str, int]


@dataclass
class SelectionCoordinationResult:
    """Schema for selection coordination results."""
    coordination_id: str
    plan: SelectionCoordinationPlan
    selected_schemas: List[str]
    selection_metadata: Dict[str, Any]
    coordination_statistics: Dict[str, float]
