"""
Schema definitions for execution safety application and enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SafetyLevel(Enum):
    """Execution safety levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SafetyCategory(Enum):
    """Execution safety categories."""
    RESOURCE_LIMITS = "resource_limits"
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    ERROR_HANDLING = "error_handling"


@dataclass
class SafetyRule:
    """Schema for individual safety rule."""
    rule_id: str
    category: SafetyCategory
    safety_level: SafetyLevel
    rule_expression: str
    auto_correctable: bool = False


@dataclass
class SafetyApplication:
    """Schema for safety application context."""
    application_id: str
    target_execution_id: str
    applied_rules: List[SafetyRule]
    application_timestamp: str
    context: Dict[str, Any]


@dataclass
class SafetyApplicationResult:
    """Schema for safety application results."""
    result_id: str
    application: SafetyApplication
    safety_passed: bool
    violations: List[Dict[str, Any]]
    auto_corrections: List[Dict[str, Any]]