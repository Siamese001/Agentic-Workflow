"""
Schema definitions for orchestration-level schema preparation orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class PreparationStrategy(Enum):
    """Orchestration preparation strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


class PreparationScope(Enum):
    """Schema preparation scopes."""
    SINGLE_SCHEMA = "single_schema"
    SCHEMA_COLLECTION = "schema_collection"
    WORKFLOW_DEPENDENT = "workflow_dependent"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class PreparationOrchestrationTask:
    """Schema for preparation orchestration task."""
    task_id: str
    preparation_type: str
    target_schemas: List[str]
    preparation_strategy: PreparationStrategy
    preparation_scope: PreparationScope


@dataclass
class PreparationOrchestrationPlan:
    """Schema for preparation orchestration plan."""
    plan_id: str
    strategy: PreparationStrategy
    scope: PreparationScope
    tasks: List[PreparationOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class PreparationOrchestrationResult:
    """Schema for preparation orchestration results."""
    orchestration_id: str
    plan: PreparationOrchestrationPlan
    prepared_schemas: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
