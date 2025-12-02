"""
Schema definitions for orchestration-level schema optimization management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class OptimizationStrategy(Enum):
    """Schema optimization strategies."""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    COST = "cost"
    QUALITY = "quality"


class ManagementScope(Enum):
    """Optimization management scopes."""
    SINGLE_COMPONENT = "single_component"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_LEVEL = "service_level"
    SYSTEM_LEVEL = "system_level"


@dataclass
class OptimizationManagementTask:
    """Schema for optimization management task."""
    task_id: str
    optimization_type: str
    target_schemas: List[str]
    optimization_strategy: OptimizationStrategy
    management_scope: ManagementScope


@dataclass
class OptimizationManagementPlan:
    """Schema for optimization management plan."""
    plan_id: str
    strategy: OptimizationStrategy
    scope: ManagementScope
    tasks: List[OptimizationManagementTask]
    resource_allocation: Dict[str, int]


@dataclass
class OptimizationManagementResult:
    """Schema for optimization management results."""
    management_id: str
    plan: OptimizationManagementPlan
    optimization_results: List[Dict[str, Any]]
    performance_improvements: Dict[str, float]
    management_statistics: Dict[str, Any]
