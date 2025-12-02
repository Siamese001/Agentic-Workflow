"""
Schema definitions for orchestration-level schema score orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class OrchestrationStrategy(Enum):
    """Score orchestration strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


class ScoreType(Enum):
    """Types of orchestrated scores."""
    QUALITY_SCORE = "quality_score"
    PERFORMANCE_SCORE = "performance_score"
    COMPLIANCE_SCORE = "compliance_score"
    RISK_SCORE = "risk_score"


@dataclass
class ScoreOrchestrationTask:
    """Schema for score orchestration task."""
    task_id: str
    score_type: ScoreType
    target_schemas: List[str]
    computation_method: str
    priority: str
    dependencies: List[str]


@dataclass
class ScoreOrchestrationPlan:
    """Schema for score orchestration plan."""
    plan_id: str
    strategy: OrchestrationStrategy
    tasks: List[ScoreOrchestrationTask]
    estimated_completion_time_ms: int
    resource_requirements: Dict[str, int]


@dataclass
class ScoreOrchestrationResult:
    """Schema for score orchestration results."""
    orchestration_id: str
    plan: ScoreOrchestrationPlan
    computed_scores: List[Dict[str, Any]]
    failed_tasks: List[str]
    orchestration_statistics: Dict[str, float]
