"""
Schema definitions for orchestration-level schema similarity management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class SimilarityStrategy(Enum):
    """Similarity management strategies."""
    PRECOMPUTED = "precomputed"
    ON_DEMAND = "on_demand"
    HYBRID = "hybrid"
    CACHED = "cached"


class ManagementScope(Enum):
    """Similarity management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    ENTERPRISE_WIDE = "enterprise_wide"
    DOMAIN_SPECIFIC = "domain_specific"


@dataclass
class SimilarityManagementTask:
    """Schema for similarity management task."""
    task_id: str
    similarity_type: str
    target_schemas: List[str]
    computation_method: str
    priority: str


@dataclass
class SimilarityManagementPlan:
    """Schema for similarity management plan."""
    plan_id: str
    strategy: SimilarityStrategy
    scope: ManagementScope
    tasks: List[SimilarityManagementTask]
    resource_allocation: Dict[str, int]


@dataclass
class SimilarityManagementResult:
    """Schema for similarity management results."""
    management_id: str
    plan: SimilarityManagementPlan
    computed_similarities: List[Dict[str, Any]]
    cache_updates: List[str]
    performance_metrics: Dict[str, float]
