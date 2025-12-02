"""
Schema definitions for execution schema validation and verification.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ValidationLevel(Enum):
    """Execution schema validation levels."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    COMPLIANCE = "compliance"


class ValidationScope(Enum):
    """Schema validation scopes."""
    SINGLE_EXECUTION = "single_execution"
    BATCH_EXECUTION = "batch_execution"
    WORKFLOW_CHAIN = "workflow_chain"
    SYSTEM_LEVEL = "system_level"


@dataclass
class SchemaValidationRule:
    """Schema for individual validation rule."""
    rule_id: str
    validation_level: ValidationLevel
    rule_expression: str
    severity: str
    auto_correctable: bool = False


@dataclass
class SchemaValidationConfig:
    """Schema for validation configuration."""
    config_id: str
    validation_levels: List[ValidationLevel]
    validation_scope: ValidationScope
    parallel_validation: bool = True
    fail_fast: bool = False


@dataclass
class SchemaValidationResult:
    """Schema for validation results."""
    result_id: str
    configuration: SchemaValidationConfig
    validation_passed: bool
    violations: List[Dict[str, Any]]
    auto_corrections: List[Dict[str, Any]]
    validation_timestamp: str