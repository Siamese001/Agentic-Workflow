"""
Schema definitions for orchestration-level schema risk orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class RiskStrategy(Enum):
    """Orchestration risk strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class RiskScope(Enum):
    """Schema risk orchestration scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class RiskOrchestrationTask:
    """Schema for risk orchestration task."""
    task_id: str
    risk_type: str
    target_schemas: List[str]
    risk_strategy: RiskStrategy
    risk_scope: RiskScope


@dataclass
class RiskOrchestrationPlan:
    """Schema for risk orchestration plan."""
    plan_id: str
    strategy: RiskStrategy
    scope: RiskScope
    tasks: List[RiskOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class RiskOrchestrationResult:
    """Schema for risk orchestration results."""
    orchestration_id: str
    plan: RiskOrchestrationPlan
    risk_results: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
