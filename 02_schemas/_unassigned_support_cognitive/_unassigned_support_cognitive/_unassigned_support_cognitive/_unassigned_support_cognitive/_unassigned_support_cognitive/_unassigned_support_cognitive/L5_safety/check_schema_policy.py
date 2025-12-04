"""
Schema definitions for schema policy checking and compliance verification.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class PolicyCategory(Enum):
    """Categories of schema policies."""
    SECURITY = "security"
    PRIVACY = "privacy"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"


class PolicyStatus(Enum):
    """Policy compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class SchemaPolicy:
    """Schema for individual policy definition."""
    policy_id: str
    category: PolicyCategory
    name: str
    description: str
    rules: List[Dict[str, Any]]
    exceptions: Optional[List[str]] = None


@dataclass
class PolicyCheck:
    """Schema for policy check execution."""
    policy: SchemaPolicy
    target_schema_id: str
    check_timestamp: str
    context: Dict[str, Any]


@dataclass
class PolicyCheckResult:
    """Schema for policy check results."""
    check_id: str
    status: PolicyStatus
    violations_found: List[Dict[str, Any]]
    recommendations: Optional[List[str]] = None
    next_review_date: Optional[str] = None