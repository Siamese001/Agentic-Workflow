"""
Schema definitions for schema safety application and enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SafetyLevel(Enum):
    """Schema safety enforcement levels."""
    PERMISSIVE = "permissive"
    STANDARD = "standard"
    RESTRICTIVE = "restrictive"
    BLOCKED = "blocked"


class SafetyCategory(Enum):
    """Safety enforcement categories."""
    CONTENT = "content"
    ACCESS = "access"
    PRIVACY = "privacy"
    SECURITY = "security"


@dataclass
class SafetyRule:
    """Schema for individual safety rule."""
    rule_id: str
    category: SafetyCategory
    safety_level: SafetyLevel
    conditions: List[Dict[str, Any]]
    actions: List[str]


@dataclass
class SafetyApplication:
    """Schema for safety application context."""
    application_id: str
    target_schema_id: str
    applied_rules: List[SafetyRule]
    enforcement_timestamp: str
    context: Dict[str, Any]


@dataclass
class SafetyApplicationResult:
    """Schema for safety application results."""
    result_id: str
    application: SafetyApplication
    violations_detected: List[Dict[str, Any]]
    actions_taken: List[str]
    overall_safety_level: SafetyLevel