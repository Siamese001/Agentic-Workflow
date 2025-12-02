"""
Schema definitions for orchestration-level schema matching coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class MatchingStrategy(Enum):
    """Orchestration matching strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    PEER_TO_PEER = "peer_to_peer"
    HIERARCHICAL = "hierarchical"


class CoordinationLevel(Enum):
    """Matching coordination levels."""
    TASK_LEVEL = "task_level"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_LEVEL = "enterprise_level"


@dataclass
class MatchingCoordinationTask:
    """Schema for matching coordination task."""
    task_id: str
    matching_type: str
    target_schemas: List[str]
    matching_strategy: MatchingStrategy
    coordination_level: CoordinationLevel


@dataclass
class MatchingCoordinationPlan:
    """Schema for matching coordination plan."""
    plan_id: str
    strategy: MatchingStrategy
    coordination_level: CoordinationLevel
    tasks: List[MatchingCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class MatchingCoordinationResult:
    """Schema for matching coordination results."""
    coordination_id: str
    plan: MatchingCoordinationPlan
    coordinated_matches: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
