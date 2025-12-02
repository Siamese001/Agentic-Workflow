"""
Schema definitions for orchestration-level schema safety management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ManagementStrategy(Enum):
    """Orchestration safety management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class ManagementScope(Enum):
    """Safety management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class SafetyManagementTask:
    """Schema for safety management task."""
    task_id: str
    safety_type: str
    target_schemas: List[str]
    management_strategy: ManagementStrategy
    management_scope: ManagementScope


@dataclass
class SafetyManagementPlan:
    """Schema for safety management plan."""
    plan_id: str
    strategy: ManagementStrategy
    scope: ManagementScope
    tasks: List[SafetyManagementTask]
    estimated_completion_time_ms: int


@dataclass
class SafetyManagementResult:
    """Schema for safety management results."""
    management_id: str
    plan: SafetyManagementPlan
    managed_safety: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
