"""
Schema definitions for orchestration-level schema failure management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class FailureStrategy(Enum):
    """Orchestration failure management strategies."""
    FAIL_FAST = "fail_fast"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAILOVER = "failover"


class ManagementScope(Enum):
    """Failure management scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class FailureManagementTask:
    """Schema for failure management task."""
    task_id: str
    failure_type: str
    management_strategy: FailureStrategy
    management_scope: ManagementScope
    recovery_procedures: List[str]


@dataclass
class FailureManagementPlan:
    """Schema for failure management plan."""
    plan_id: str
    strategy: FailureStrategy
    scope: ManagementScope
    tasks: List[FailureManagementTask]
    recovery_time_estimates: Dict[str, int]


@dataclass
class FailureManagementResult:
    """Schema for failure management results."""
    management_id: str
    plan: FailureManagementPlan
    managed_failures: List[Dict[str, Any]]
    recovery_actions: List[str]
    management_statistics: Dict[str, Any]
