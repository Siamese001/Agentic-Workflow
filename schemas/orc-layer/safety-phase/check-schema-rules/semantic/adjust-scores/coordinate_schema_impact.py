"""
Schema definitions for orchestration-level schema impact coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ImpactStrategy(Enum):
    """Orchestration impact strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class CoordinationLevel(Enum):
    """Impact coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class ImpactCoordinationTask:
    """Schema for impact coordination task."""
    task_id: str
    impact_type: str
    target_schemas: List[str]
    impact_strategy: ImpactStrategy
    coordination_level: CoordinationLevel


@dataclass
class ImpactCoordinationPlan:
    """Schema for impact coordination plan."""
    plan_id: str
    strategy: ImpactStrategy
    coordination_level: CoordinationLevel
    tasks: List[ImpactCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class ImpactCoordinationResult:
    """Schema for impact coordination results."""
    coordination_id: str
    plan: ImpactCoordinationPlan
    coordinated_impacts: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
