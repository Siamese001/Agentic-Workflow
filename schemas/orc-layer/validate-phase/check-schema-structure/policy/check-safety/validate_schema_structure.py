"""
Schema definitions for orchestration-level schema structure validation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ValidationLevel(Enum):
    """Structure validation levels."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    INTEGRATION = "integration"
    ORCHESTRATION = "orchestration"


class ValidationScope(Enum):
    """Structure validation scopes."""
    SINGLE_SCHEMA = "single_schema"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class StructureValidationRule:
    """Schema for structure validation rule."""
    rule_id: str
    validation_level: ValidationLevel
    rule_expression: str
    severity: str
    auto_correctable: bool = False


@dataclass
class StructureValidationConfig:
    """Schema for structure validation configuration."""
    validation_levels: List[ValidationLevel]
    validation_scope: ValidationScope
    parallel_validation: bool = True
    fail_fast: bool = False


@dataclass
class StructureValidationResult:
    """Schema for structure validation results."""
    validation_id: str
    configuration: StructureValidationConfig
    validation_passed: bool
    violations: List[Dict[str, Any]]
    auto_corrections: List[Dict[str, Any]]
    validation_timestamp: str
