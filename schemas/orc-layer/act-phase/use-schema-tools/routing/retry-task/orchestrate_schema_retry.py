"""
Schema definitions for orchestration-level schema retry orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class RetryStrategy(Enum):
    """Orchestration retry strategies."""
    GLOBAL_RETRY = "global_retry"
    LOCAL_RETRY = "local_retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    ADAPTIVE_RETRY = "adaptive_retry"


class RetryScope(Enum):
    """Retry orchestration scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class RetryOrchestrationTask:
    """Schema for retry orchestration task."""
    task_id: str
    original_task_id: str
    retry_strategy: RetryStrategy
    retry_scope: RetryScope
    max_attempts: int
    backoff_strategy: str


@dataclass
class RetryOrchestrationPlan:
    """Schema for retry orchestration plan."""
    plan_id: str
    strategy: RetryStrategy
    scope: RetryScope
    tasks: List[RetryOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class RetryOrchestrationResult:
    """Schema for retry orchestration results."""
    orchestration_id: str
    plan: RetryOrchestrationPlan
    successful_retries: List[str]
    failed_retries: List[str]
    retry_statistics: Dict[str, Any]
