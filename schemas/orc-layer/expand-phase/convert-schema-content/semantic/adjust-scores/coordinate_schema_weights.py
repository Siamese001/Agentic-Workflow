"""
Schema definitions for orchestration-level schema weight coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class CoordinationMethod(Enum):
    """Weight coordination methods."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CONSENSUS = "consensus"
    HIERARCHICAL = "hierarchical"


class WeightScope(Enum):
    """Weight coordination scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    DEPARTMENTAL = "departmental"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class WeightCoordinationTask:
    """Schema for weight coordination task."""
    task_id: str
    weight_category: str
    target_components: List[str]
    coordination_method: CoordinationMethod
    consensus_requirements: Dict[str, Any]


@dataclass
class WeightCoordinationPlan:
    """Schema for weight coordination plan."""
    plan_id: str
    coordination_method: CoordinationMethod
    scope: WeightScope
    tasks: List[WeightCoordinationTask]
    estimated_time_ms: int


@dataclass
class WeightCoordinationResult:
    """Schema for weight coordination results."""
    coordination_id: str
    plan: WeightCoordinationPlan
    coordinated_weights: List[Dict[str, Any]]
    consensus_achieved: bool
    coordination_metadata: Dict[str, Any]
