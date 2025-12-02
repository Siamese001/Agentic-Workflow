"""
Schema definitions for orchestration-level schema ranking orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RankingStrategy(Enum):
    """Orchestration ranking strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class RankingScope(Enum):
    """Schema ranking scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    CROSS_DOMAIN = "cross_domain"


@dataclass
class RankingOrchestrationTask:
    """Schema for ranking orchestration task."""
    task_id: str
    ranking_criteria: List[str]
    target_schemas: List[str]
    ranking_method: str
    priority: str
    dependencies: List[str]


@dataclass
class RankingOrchestrationPlan:
    """Schema for ranking orchestration plan."""
    plan_id: str
    strategy: RankingStrategy
    scope: RankingScope
    tasks: List[RankingOrchestrationTask]
    estimated_completion_time_ms: int


@dataclass
class RankingOrchestrationResult:
    """Schema for ranking orchestration results."""
    orchestration_id: str
    plan: RankingOrchestrationPlan
    ranked_schemas: List[Dict[str, Any]]
    task_completion_status: Dict[str, str]
    orchestration_metrics: Dict[str, float]
