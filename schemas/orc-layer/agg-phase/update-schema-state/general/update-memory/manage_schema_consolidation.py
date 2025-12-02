"""
Schema definitions for orchestration-level schema consolidation management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ManagementStrategy(Enum):
    """Orchestration consolidation management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    BATCH_PROCESSED = "batch_processed"
    STREAMING = "streaming"


class ManagementScope(Enum):
    """Consolidation management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class ConsolidationManagementTask:
    """Schema for consolidation management task."""
    task_id: str
    consolidation_type: str
    target_schemas: List[str]
    management_strategy: ManagementStrategy
    management_scope: ManagementScope


@dataclass
class ConsolidationManagementPlan:
    """Schema for consolidation management plan."""
    plan_id: str
    strategy: ManagementStrategy
    scope: ManagementScope
    tasks: List[ConsolidationManagementTask]
    estimated_completion_time_ms: int


@dataclass
class ConsolidationManagementResult:
    """Schema for consolidation management results."""
    management_id: str
    plan: ConsolidationManagementPlan
    managed_consolidations: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
