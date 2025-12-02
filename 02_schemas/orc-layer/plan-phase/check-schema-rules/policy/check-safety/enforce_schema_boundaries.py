"""
Schema definitions for orchestration-level schema boundary enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class BoundaryType(Enum):
    """Orchestration boundary types."""
    SERVICE_BOUNDARY = "service_boundary"
    WORKFLOW_BOUNDARY = "workflow_boundary"
    RESOURCE_BOUNDARY = "resource_boundary"
    SECURITY_BOUNDARY = "security_boundary"


class EnforcementAction(Enum):
    """Boundary enforcement actions."""
    ALLOW = "allow"
    DENY = "deny"
    QUEUE = "queue"
    ESCALATE = "escalate"
    LOG_ONLY = "log_only"


@dataclass
class OrchestrationBoundary:
    """Schema for orchestration boundary."""
    boundary_id: str
    boundary_type: BoundaryType
    scope_definition: Dict[str, Any]
    allowed_operations: List[str]
    forbidden_operations: List[str]
    default_action: EnforcementAction


@dataclass
class BoundaryEnforcementConfig:
    notification_channels: List[str]
    strict_mode: bool = True
    audit_violations: bool = True
    automatic_recovery: bool = False
    """Schema for boundary enforcement configuration."""


@dataclass
class BoundaryViolation:
    """Schema for boundary violation details."""
    violation_id: str
    boundary_id: str
    violating_operation: str
    violation_context: Dict[str, Any]
    timestamp: str


@dataclass
class BoundaryEnforcementResult:
    """Schema for boundary enforcement results."""
    enforcement_id: str
    violations: List[BoundaryViolation]
    actions_taken: List[EnforcementAction]
    enforcement_metadata: Dict[str, Any]
