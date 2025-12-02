"""
Schema definitions for orchestration-level schema safety orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SafetyStrategy(Enum):
    """Orchestration safety strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class SafetyScope(Enum):
    """Schema safety orchestration scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class SafetyOrchestrationTask:
    """Schema for safety orchestration task."""
    task_id: str
    safety_type: str
    target_schemas: List[str]
    safety_strategy: SafetyStrategy
    safety_scope: SafetyScope


@dataclass
class SafetyOrchestrationPlan:
    """Schema for safety orchestration plan."""
    plan_id: str
    strategy: SafetyStrategy
    scope: SafetyScope
    tasks: List[SafetyOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class SafetyOrchestrationResult:
    """Schema for safety orchestration results."""
    orchestration_id: str
    plan: SafetyOrchestrationPlan
    safety_results: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
