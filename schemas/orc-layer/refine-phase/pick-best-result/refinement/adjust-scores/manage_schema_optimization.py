"""
Schema definitions for orchestration-level schema optimization management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class OptimizationType(Enum):
    """Schema optimization types."""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    COST = "cost"
    QUALITY = "quality"


class ManagementMode(Enum):
    """Optimization management modes."""
    PROACTIVE = "proactive"
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive"


@dataclass
class OptimizationManagementTask:
    """Schema for optimization management task."""
    task_id: str
    optimization_type: OptimizationType
    target_schemas: List[str]
    management_mode: ManagementMode
    optimization_parameters: Dict[str, Any]


@dataclass
class OptimizationManagementPlan:
    """Schema for optimization management plan."""
    plan_id: str
    optimization_type: OptimizationType
    management_mode: ManagementMode
    tasks: List[OptimizationManagementTask]
    resource_allocation: Dict[str, int]


@dataclass
class OptimizationManagementResult:
    """Schema for optimization management results."""
    management_id: str
    plan: OptimizationManagementPlan
    optimization_results: List[Dict[str, Any]]
    performance_gains: Dict[str, float]
    management_statistics: Dict[str, Any]
