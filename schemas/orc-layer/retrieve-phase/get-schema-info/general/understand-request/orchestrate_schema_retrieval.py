"""
Schema definitions for orchestration-level schema retrieval orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RetrievalStrategy(Enum):
    """Orchestration retrieval strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CACHED = "cached"
    STREAMING = "streaming"


class RetrievalScope(Enum):
    """Schema retrieval scopes."""
    SINGLE_SCHEMA = "single_schema"
    SCHEMA_COLLECTION = "schema_collection"
    WORKFLOW_DEPENDENT = "workflow_dependent"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class RetrievalOrchestrationTask:
    """Schema for retrieval orchestration task."""
    task_id: str
    retrieval_type: str
    target_schemas: List[str]
    retrieval_strategy: RetrievalStrategy
    retrieval_scope: RetrievalScope


@dataclass
class RetrievalOrchestrationPlan:
    """Schema for retrieval orchestration plan."""
    plan_id: str
    strategy: RetrievalStrategy
    scope: RetrievalScope
    tasks: List[RetrievalOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class RetrievalOrchestrationResult:
    """Schema for retrieval orchestration results."""
    orchestration_id: str
    plan: RetrievalOrchestrationPlan
    retrieved_schemas: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
