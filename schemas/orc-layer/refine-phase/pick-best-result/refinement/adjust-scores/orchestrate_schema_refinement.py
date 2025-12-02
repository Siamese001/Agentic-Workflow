"""
Schema definitions for orchestration-level schema refinement orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RefinementStrategy(Enum):
    """Schema refinement strategies."""
    ITERATIVE = "iterative"
    GENETIC = "genetic"
    GRADIENT_BASED = "gradient_based"
    HYBRID = "hybrid"


class OrchestrationMode(Enum):
    """Refinement orchestration modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


@dataclass
class RefinementOrchestrationTask:
    """Schema for refinement orchestration task."""
    task_id: str
    refinement_type: str
    target_schemas: List[str]
    refinement_strategy: RefinementStrategy
    orchestration_mode: OrchestrationMode


@dataclass
class RefinementOrchestrationPlan:
    """Schema for refinement orchestration plan."""
    plan_id: str
    strategy: RefinementStrategy
    mode: OrchestrationMode
    tasks: List[RefinementOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class RefinementOrchestrationResult:
    """Schema for refinement orchestration results."""
    orchestration_id: str
    plan: RefinementOrchestrationPlan
    refined_schemas: List[Dict[str, Any]]
    convergence_metrics: Dict[str, float]
    orchestration_statistics: Dict[str, Any]
