"""
Schema definitions for orchestration-level schema aggregation orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class AggregationStrategy(Enum):
    """Orchestration aggregation strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class AggregationScope(Enum):
    """Schema aggregation scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class AggregationOrchestrationTask:
    """Schema for aggregation orchestration task."""
    task_id: str
    aggregation_type: str
    target_schemas: List[str]
    aggregation_strategy: AggregationStrategy
    aggregation_scope: AggregationScope


@dataclass
class AggregationOrchestrationPlan:
    """Schema for aggregation orchestration plan."""
    plan_id: str
    strategy: AggregationStrategy
    scope: AggregationScope
    tasks: List[AggregationOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class AggregationOrchestrationResult:
    """Schema for aggregation orchestration results."""
    orchestration_id: str
    plan: AggregationOrchestrationPlan
    aggregated_schemas: List[Dict[str, Any]]
    orchestration_statistics: Dict[str, Any]
