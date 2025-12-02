"""
Schema definitions for schema validation and structure verification.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ValidationLevel(Enum):
    """Schema validation levels."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    BUSINESS_RULES = "business_rules"


class ValidationSeverity(Enum):
    """Validation rule severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Schema for individual validation rule."""
    rule_id: str
    rule_type: ValidationLevel
    severity: ValidationSeverity
    description: str
    parameters: Dict[str, Any]


@dataclass
class ValidationResult:
    """Schema for validation result details."""
    rule_id: str
    is_valid: bool
    message: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class SchemaValidationReport:
    """Schema for complete validation report."""
    schema_id: str
    validation_timestamp: str
    total_rules_checked: int
    passed_rules: int
    failed_rules: int
    results: List[ValidationResult]
    overall_valid: bool