"""
Schema definitions for orchestration-level schema adjustment coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class AdjustmentStrategy(Enum):
    """Schema adjustment strategies."""
    AUTOMATIC = "automatic"
    MANUAL_APPROVAL = "manual_approval"
    CONSENSUS_BASED = "consensus_based"
    ROLLING = "rolling"


class CoordinationLevel(Enum):
    """Adjustment coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class AdjustmentCoordinationTask:
    """Schema for adjustment coordination task."""
    task_id: str
    adjustment_type: str
    target_schemas: List[str]
    adjustment_strategy: AdjustmentStrategy
    coordination_level: CoordinationLevel


@dataclass
class AdjustmentCoordinationPlan:
    """Schema for adjustment coordination plan."""
    plan_id: str
    strategy: AdjustmentStrategy
    coordination_level: CoordinationLevel
    tasks: List[AdjustmentCoordinationTask]
    approval_requirements: Dict[str, bool]


@dataclass
class AdjustmentCoordinationResult:
    """Schema for adjustment coordination results."""
    coordination_id: str
    plan: AdjustmentCoordinationPlan
    adjusted_schemas: List[Dict[str, Any]]
    approval_status: Dict[str, bool]
    coordination_metadata: Dict[str, Any]
