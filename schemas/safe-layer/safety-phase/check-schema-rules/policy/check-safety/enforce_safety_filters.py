"""
Schema definitions for safety filter enforcement and application.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class FilterCategory(Enum):
    """Safety filter categories."""
    CONTENT = "content"
    ACCESS = "access"
    PRIVACY = "privacy"
    SECURITY = "security"


class EnforcementLevel(Enum):
    """Filter enforcement levels."""
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKING = "blocking"
    CRITICAL = "critical"


@dataclass
class SafetyFilter:
    """Schema for individual safety filter."""
    filter_id: str
    category: FilterCategory
    filter_rules: List[Dict[str, Any]]
    enforcement_level: EnforcementLevel
    priority: int = 0


@dataclass
class FilterEnforcement:
    """Schema for filter enforcement context."""
    enforcement_id: str
    target_schema_id: str
    applied_filters: List[SafetyFilter]
    enforcement_timestamp: str
    context: Dict[str, Any]


@dataclass
class FilterEnforcementResult:
    """Schema for filter enforcement results."""
    result_id: str
    enforcement: FilterEnforcement
    violations_detected: List[str]
    filters_triggered: List[str]
    enforcement_successful: bool