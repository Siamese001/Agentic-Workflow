"""
Schema definitions for orchestration-level schema logging management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class LoggingStrategy(Enum):
    """Orchestration logging strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"
    EVENT_STREAMING = "event_streaming"


class ManagementScope(Enum):
    """Logging management scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_LEVEL = "service_level"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class LoggingManagementTask:
    """Schema for logging management task."""
    task_id: str
    logging_type: str
    target_components: List[str]
    logging_strategy: LoggingStrategy
    management_scope: ManagementScope


@dataclass
class LoggingManagementPlan:
    """Schema for logging management plan."""
    plan_id: str
    strategy: LoggingStrategy
    scope: ManagementScope
    tasks: List[LoggingManagementTask]
    resource_requirements: Dict[str, int]


@dataclass
class LoggingManagementResult:
    """Schema for logging management results."""
    management_id: str
    plan: LoggingManagementPlan
    managed_logs: List[Dict[str, Any]]
    logging_statistics: Dict[str, Any]
