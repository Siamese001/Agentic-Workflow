"""
Schema definitions for orchestration-level schema retrieval operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class OrchestrationMode(Enum):
    """Schema retrieval orchestration modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


class RetrievalPriority(Enum):
    """Retrieval operation priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class RetrievalTask:
    """Schema for individual retrieval task."""
    task_id: str
    schema_id: str
    retrieval_type: str
    priority: RetrievalPriority
    dependencies: List[str]
    estimated_duration_ms: int


@dataclass
class OrchestrationPlan:
    """Schema for retrieval orchestration plan."""
    plan_id: str
    mode: OrchestrationMode
    tasks: List[RetrievalTask]
    total_estimated_time_ms: int
    resource_requirements: Dict[str, int]


@dataclass
class OrchestrationResult:
    """Schema for orchestration execution results."""
    orchestration_id: str
    plan: OrchestrationPlan
    completed_tasks: List[str]
    failed_tasks: List[str]
    execution_time_ms: int
    resource_usage: Dict[str, int]
