"""
Schema definitions for orchestration-level schema ethics management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class EthicsStrategy(Enum):
    """Orchestration ethics management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    CONSENSUS_BASED = "consensus_based"
    HIERARCHICAL = "hierarchical"


class ManagementScope(Enum):
    """Ethics management scopes."""
    SINGLE_WORKFLOW = "single_workflow"
    CROSS_WORKFLOW = "cross_workflow"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class EthicsManagementTask:
    """Schema for ethics management task."""
    task_id: str
    ethics_type: str
    target_schemas: List[str]
    ethics_strategy: EthicsStrategy
    management_scope: ManagementScope


@dataclass
class EthicsManagementPlan:
    """Schema for ethics management plan."""
    plan_id: str
    strategy: EthicsStrategy
    scope: ManagementScope
    tasks: List[EthicsManagementTask]
    estimated_completion_time_ms: int


@dataclass
class EthicsManagementResult:
    """Schema for ethics management results."""
    management_id: str
    plan: EthicsManagementPlan
    managed_ethics: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
