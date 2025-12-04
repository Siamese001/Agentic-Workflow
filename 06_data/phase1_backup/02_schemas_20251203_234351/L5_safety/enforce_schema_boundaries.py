"""
Schema definitions for schema boundary enforcement and containment.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class BoundaryType(Enum):
    """Types of schema boundaries."""
    NAMESPACE = "namespace"
    ACCESS_LEVEL = "access_level"
    DATA_SCOPE = "data_scope"
    RESOURCE_LIMIT = "resource_limit"


class EnforcementAction(Enum):
    """Boundary enforcement actions."""
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"
    ESCALATE = "escalate"


@dataclass
class SchemaBoundary:
    """Schema for individual boundary definition."""
    boundary_id: str
    boundary_type: BoundaryType
    scope: str
    constraints: Dict[str, Any]
    enforcement_action: EnforcementAction


@dataclass
class BoundaryViolation:
    """Schema for boundary violation details."""
    boundary_id: str
    violator_schema_id: str
    violation_type: str
    severity: str
    description: str


@dataclass
class BoundaryEnforcementResult:
    """Schema for boundary enforcement results."""
    enforcement_id: str
    violations: List[BoundaryViolation]
    actions_taken: List[EnforcementAction]
    enforcement_timestamp: str