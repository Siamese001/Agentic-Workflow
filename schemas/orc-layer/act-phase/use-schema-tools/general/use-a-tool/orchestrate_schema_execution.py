"""
Schema definitions for orchestration-level schema execution operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ExecutionStrategy(Enum):
    """Schema execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


class ExecutionScope(Enum):
    """Schema execution scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    DISTRIBUTED = "distributed"


@dataclass
class ExecutionTask:
    """Schema for individual execution task."""
    task_id: str
    schema_id: str
    execution_type: str
    dependencies: List[str]
    resource_requirements: Dict[str, int]
    priority: str


@dataclass
class ExecutionOrchestration:
    """Schema for execution orchestration."""
    orchestration_id: str
    strategy: ExecutionStrategy
    scope: ExecutionScope
    tasks: List[ExecutionTask]
    total_estimated_time_ms: int


@dataclass
class ExecutionOrchestrationResult:
    """Schema for execution orchestration results."""
    result_id: str
    orchestration: ExecutionOrchestration
    completed_tasks: List[str]
    failed_tasks: List[str]
    execution_statistics: Dict[str, Any]
