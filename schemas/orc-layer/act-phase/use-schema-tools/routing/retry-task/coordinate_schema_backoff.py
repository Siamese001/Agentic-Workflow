"""
Schema definitions for orchestration-level schema backoff coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class BackoffStrategy(Enum):
    """Orchestration backoff strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    ADAPTIVE_BACKOFF = "adaptive_backoff"


class CoordinationLevel(Enum):
    """Backoff coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class BackoffCoordinationTask:
    """Schema for backoff coordination task."""
    task_id: str
    backoff_strategy: BackoffStrategy
    coordination_level: CoordinationLevel
    initial_delay_ms: int
    maximum_delay_ms: int


@dataclass
class BackoffCoordinationPlan:
    """Schema for backoff coordination plan."""
    plan_id: str
    strategy: BackoffStrategy
    coordination_level: CoordinationLevel
    tasks: List[BackoffCoordinationTask]
    estimated_total_delay_ms: int


@dataclass
class BackoffCoordinationResult:
    """Schema for backoff coordination results."""
    coordination_id: str
    plan: BackoffCoordinationPlan
    coordinated_backoffs: List[Dict[str, Any]]
    total_delay_applied_ms: int
    coordination_statistics: Dict[str, Any]
