"""
Schema definitions for execution compliance checking and validation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ComplianceType(Enum):
    """Execution compliance types."""
    REGULATORY = "regulatory"
    INDUSTRY = "industry"
    ORGANIZATIONAL = "organizational"
    TECHNICAL = "technical"


class CheckLevel(Enum):
    """Compliance check levels."""
    COMPREHENSIVE = "comprehensive"
    STANDARD = "standard"
    BASIC = "basic"
    MINIMAL = "minimal"


@dataclass
class ComplianceCheck:
    """Schema for individual compliance check."""
    check_id: str
    compliance_type: ComplianceType
    check_level: CheckLevel
    check_criteria: Dict[str, Any]
    mandatory: bool = True


@dataclass
class ComplianceCheckContext:
    """Schema for compliance check context."""
    context_id: str
    target_execution_id: str
    checks_performed: List[ComplianceCheck]
    check_timestamp: str
    check_environment: Dict[str, Any]


@dataclass
class ComplianceCheckResult:
    """Schema for compliance check results."""
    result_id: str
    context: ComplianceCheckContext
    compliance_passed: bool
    violations: List[Dict[str, Any]]
    compliance_score: float