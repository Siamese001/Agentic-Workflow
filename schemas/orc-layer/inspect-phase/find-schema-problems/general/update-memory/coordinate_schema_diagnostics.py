"""
Schema definitions for orchestration-level schema diagnostics coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class CoordinationStrategy(Enum):
    """Diagnostics coordination strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    EVENT_DRIVEN = "event_driven"
    POLLING_BASED = "polling_based"


class DiagnosticScope(Enum):
    """Diagnostics coordination scopes."""
    SINGLE_COMPONENT = "single_component"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class DiagnosticCoordinationTask:
    """Schema for diagnostic coordination task."""
    task_id: str
    diagnostic_type: str
    target_components: List[str]
    coordination_strategy: CoordinationStrategy
    diagnostic_scope: DiagnosticScope


@dataclass
class DiagnosticCoordinationPlan:
    """Schema for diagnostic coordination plan."""
    plan_id: str
    strategy: CoordinationStrategy
    scope: DiagnosticScope
    tasks: List[DiagnosticCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class DiagnosticCoordinationResult:
    """Schema for diagnostic coordination results."""
    coordination_id: str
    plan: DiagnosticCoordinationPlan
    coordinated_diagnostics: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
