"""
Schema definitions for orchestration-level schema inspection orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class InspectionStrategy(Enum):
    """Orchestration inspection strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class InspectionScope(Enum):
    """Schema inspection scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class InspectionOrchestrationTask:
    """Schema for inspection orchestration task."""
    task_id: str
    inspection_type: str
    target_schemas: List[str]
    inspection_strategy: InspectionStrategy
    inspection_scope: InspectionScope


@dataclass
class InspectionOrchestrationPlan:
    """Schema for inspection orchestration plan."""
    plan_id: str
    strategy: InspectionStrategy
    scope: InspectionScope
    tasks: List[InspectionOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class InspectionOrchestrationResult:
    """Schema for inspection orchestration results."""
    orchestration_id: str
    plan: InspectionOrchestrationPlan
    inspection_results: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
