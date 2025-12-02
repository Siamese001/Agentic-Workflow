"""
Schema definitions for orchestration-level schema dependency management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ManagementStrategy(Enum):
    """Orchestration dependency management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"


class DependencyScope(Enum):
    """Dependency management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class DependencyManagementTask:
    """Schema for dependency management task."""
    task_id: str
    dependency_type: str
    target_schemas: List[str]
    management_strategy: ManagementStrategy
    dependency_scope: DependencyScope


@dataclass
class DependencyManagementPlan:
    """Schema for dependency management plan."""
    plan_id: str
    strategy: ManagementStrategy
    scope: DependencyScope
    tasks: List[DependencyManagementTask]
    estimated_completion_time_ms: int


@dataclass
class DependencyManagementResult:
    """Schema for dependency management results."""
    management_id: str
    plan: DependencyManagementPlan
    managed_dependencies: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
