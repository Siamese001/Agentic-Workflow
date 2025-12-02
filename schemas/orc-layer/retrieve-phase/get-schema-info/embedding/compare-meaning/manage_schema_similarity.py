"""
Schema definitions for orchestration-level schema similarity management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ManagementStrategy(Enum):
    """Orchestration similarity management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CACHED = "cached"
    STREAMING = "streaming"


class ManagementScope(Enum):
    """Similarity management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class SimilarityManagementTask:
    """Schema for similarity management task."""
    task_id: str
    similarity_type: str
    target_schemas: List[str]
    management_strategy: ManagementStrategy
    management_scope: ManagementScope


@dataclass
class SimilarityManagementPlan:
    """Schema for similarity management plan."""
    plan_id: str
    strategy: ManagementStrategy
    scope: ManagementScope
    tasks: List[SimilarityManagementTask]
    estimated_completion_time_ms: int


@dataclass
class SimilarityManagementResult:
    """Schema for similarity management results."""
    management_id: str
    plan: SimilarityManagementPlan
    managed_similarities: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
