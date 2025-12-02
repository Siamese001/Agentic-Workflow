"""
Schema definitions for orchestration-level schema service coordination.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class CoordinationStrategy(Enum):
    """Service coordination strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    PEER_TO_PEER = "peer_to_peer"
    HIERARCHICAL = "hierarchical"


class ServiceType(Enum):
    """Types of coordinated services."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    GENERATION = "generation"
    ANALYSIS = "analysis"


@dataclass
class ServiceCoordinationTask:
    """Schema for service coordination task."""
    task_id: str
    service_type: ServiceType
    target_schemas: List[str]
    coordination_strategy: CoordinationStrategy
    service_endpoints: List[str]


@dataclass
class ServiceCoordinationPlan:
    """Schema for service coordination plan."""
    plan_id: str
    strategy: CoordinationStrategy
    service_types: List[ServiceType]
    tasks: List[ServiceCoordinationTask]
    estimated_completion_time_ms: int


@dataclass
class ServiceCoordinationResult:
    """Schema for service coordination results."""
    coordination_id: str
    plan: ServiceCoordinationPlan
    coordinated_services: List[str]
    service_interactions: List[Dict[str, Any]]
    coordination_statistics: Dict[str, Any]
