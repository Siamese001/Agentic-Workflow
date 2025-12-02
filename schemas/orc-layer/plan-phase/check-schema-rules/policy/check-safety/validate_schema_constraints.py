"""
Schema definitions for orchestration-level schema constraint validation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ConstraintCategory(Enum):
    """Orchestration constraint categories."""
    WORKFLOW = "workflow"
    RESOURCE = "resource"
    SECURITY = "security"
    PERFORMANCE = "performance"


class ValidationScope(Enum):
    """Constraint validation scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTIRE_ORCHESTRATION = "entire_orchestration"


@dataclass
class OrchestrationConstraint:
    """Schema for orchestration constraint."""
    constraint_id: str
    category: ConstraintCategory
    scope: ValidationScope
    rule_expression: str
    severity: str
    action_on_violation: str


@dataclass
class ConstraintValidationConfig:
    """Schema for constraint validation configuration."""
    validation_scope: ValidationScope
    parallel_validation: bool = True
    fail_fast: bool = False
    generate_reports: bool = True


@dataclass
class ConstraintViolation:
    """Schema for constraint violation details."""
    violation_id: str
    constraint_id: str
    violating_element: str
    violation_details: Dict[str, Any]
    recommended_action: str


@dataclass
class ConstraintValidationResult:
    """Schema for constraint validation results."""
    validation_id: str
    configuration: ConstraintValidationConfig
    violations: List[ConstraintViolation]
    validation_passed: bool
    validation_timestamp: str
