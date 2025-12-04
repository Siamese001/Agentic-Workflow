"""
Schema definitions for safety ethics validation and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class EthicsDomain(Enum):
    """Safety ethics validation domains."""
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"


class ComplianceStatus(Enum):
    """Ethics compliance status."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class EthicsRule:
    """Schema for individual ethics rule."""
    rule_id: str
    domain: EthicsDomain
    rule_expression: str
    severity: str
    validation_criteria: Dict[str, Any]


@dataclass
class EthicsValidation:
    """Schema for ethics validation context."""
    validation_id: str
    target_schema_id: str
    rules_applied: List[EthicsRule]
    validation_timestamp: str
    validation_context: Dict[str, Any]


@dataclass
class EthicsValidationResult:
    """Schema for ethics validation results."""
    result_id: str
    validation: EthicsValidation
    compliance_status: ComplianceStatus
    violations: List[Dict[str, Any]]
    recommendations: List[str]