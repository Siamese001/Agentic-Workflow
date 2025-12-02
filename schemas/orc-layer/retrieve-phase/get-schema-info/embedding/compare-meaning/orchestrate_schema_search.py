"""
Schema definitions for orchestration-level schema search orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SearchStrategy(Enum):
    """Orchestration search strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    INDEXED = "indexed"
    HYBRID = "hybrid"


class SearchScope(Enum):
    """Schema search scopes."""
    SINGLE_COLLECTION = "single_collection"
    MULTI_COLLECTION = "multi_collection"
    WORKFLOW_SPECIFIC = "workflow_specific"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class SearchOrchestrationTask:
    """Schema for search orchestration task."""
    task_id: str
    search_type: str
    search_criteria: Dict[str, Any]
    search_strategy: SearchStrategy
    search_scope: SearchScope


@dataclass
class SearchOrchestrationPlan:
    """Schema for search orchestration plan."""
    plan_id: str
    strategy: SearchStrategy
    scope: SearchScope
    tasks: List[SearchOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class SearchOrchestrationResult:
    """Schema for search orchestration results."""
    orchestration_id: str
    plan: SearchOrchestrationPlan
    search_results: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
