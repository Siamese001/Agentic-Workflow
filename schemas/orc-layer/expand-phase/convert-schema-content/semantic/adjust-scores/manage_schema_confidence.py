"""
Schema definitions for orchestration-level schema confidence management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ConfidenceStrategy(Enum):
    """Confidence management strategies."""
    AGGREGATE = "aggregate"
    WEIGHTED_AVERAGE = "weighted_average"
    BAYESIAN = "bayesian"
    ENSEMBLE = "ensemble"


class ManagementLevel(Enum):
    """Confidence management levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class ConfidenceManagementTask:
    """Schema for confidence management task."""
    task_id: str
    confidence_source: str
    target_schemas: List[str]
    computation_strategy: ConfidenceStrategy
    management_level: ManagementLevel


@dataclass
class ConfidenceManagementPlan:
    """Schema for confidence management plan."""
    plan_id: str
    strategy: ConfidenceStrategy
    management_level: ManagementLevel
    tasks: List[ConfidenceManagementTask]
    resource_allocation: Dict[str, int]


@dataclass
class ConfidenceManagementResult:
    """Schema for confidence management results."""
    management_id: str
    plan: ConfidenceManagementPlan
    managed_confidence_scores: List[Dict[str, Any]]
    aggregation_results: Dict[str, float]
    management_statistics: Dict[str, Any]
