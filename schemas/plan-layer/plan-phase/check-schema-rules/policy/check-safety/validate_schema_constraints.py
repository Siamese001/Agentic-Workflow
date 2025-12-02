"""
Schema definitions for schema constraint validation and enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ConstraintType(Enum):
    """Types of schema constraints."""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"


class ConstraintSeverity(Enum):
    """Constraint violation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SchemaConstraint:
    """Schema for individual constraint definition."""
    constraint_id: str
    constraint_type: ConstraintType
    field_path: str
    parameters: Dict[str, Any]
    severity: ConstraintSeverity
    message_template: str


@dataclass
class ConstraintViolation:
    """Schema for constraint violation details."""
    constraint_id: str
    field_path: str
    actual_value: Union[str, int, float, bool, List[Any]]
    expected_value: Optional[Union[str, int, float, bool, List[Any]]] = None
    message: str
    severity: ConstraintSeverity


@dataclass
class ConstraintValidationResult:
    """Schema for constraint validation results."""
    schema_id: str
    is_valid: bool
    violations: List[ConstraintViolation]
    validation_timestamp: str
    total_constraints_checked: int