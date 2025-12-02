"""
Schema definitions for orchestration-level schema response management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ResponseStrategy(Enum):
    """Response management strategies."""
    IMMEDIATE = "immediate"
    BATCHED = "batched"
    STREAMING = "streaming"
    QUEUED = "queued"


class ManagementScope(Enum):
    """Response management scopes."""
    SINGLE_SERVICE = "single_service"
    WORKFLOW_LEVEL = "workflow_level"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class ResponseManagementTask:
    """Schema for response management task."""
    task_id: str
    response_type: str
    source_service: str
    management_strategy: ResponseStrategy
    management_scope: ManagementScope


@dataclass
class ResponseManagementPlan:
    """Schema for response management plan."""
    plan_id: str
    strategy: ResponseStrategy
    scope: ManagementScope
    tasks: List[ResponseManagementTask]
    resource_requirements: Dict[str, int]


@dataclass
class ResponseManagementResult:
    """Schema for response management results."""
    management_id: str
    plan: ResponseManagementPlan
    managed_responses: List[Dict[str, Any]]
    processing_statistics: Dict[str, float]
    management_metadata: Dict[str, Any]
