"""
Schema definitions for safety policy application and validation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class SafetyLevel(Enum):
    """Safety policy enforcement levels."""
    PERMISSIVE = "permissive"
    STANDARD = "standard"
    RESTRICTIVE = "restrictive"
    BLOCKED = "blocked"


class PolicyType(Enum):
    """Types of safety policies."""
    CONTENT_FILTER = "content_filter"
    ACCESS_CONTROL = "access_control"
    RATE_LIMITING = "rate_limiting"
    DATA_PROTECTION = "data_protection"


@dataclass
class SafetyPolicy:
    """Schema for safety policy definition."""
    policy_id: str
    policy_type: PolicyType
    safety_level: SafetyLevel
    rules: List[Dict[str, Any]]
    exceptions: Optional[List[str]] = None


@dataclass
class PolicyApplication:
    """Schema for policy application context."""
    policy: SafetyPolicy
    target_schema_id: str
    context: Dict[str, Any]
    enforcement_timestamp: str


@dataclass
class SafetyPolicyResult:
    """Schema for safety policy application result."""
    application_id: str
    policy_applied: bool
    safety_level_assigned: SafetyLevel
    violations: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None