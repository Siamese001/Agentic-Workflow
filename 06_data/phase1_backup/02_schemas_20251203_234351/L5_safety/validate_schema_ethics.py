"""
Schema definitions for schema ethics validation and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class EthicsCategory(Enum):
    """Ethics validation categories."""
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    BIAS_DETECTION = "bias_detection"


class ComplianceLevel(Enum):
    """Ethics compliance levels."""
    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class EthicsRule:
    """Schema for individual ethics rule."""
    rule_id: str
    category: EthicsCategory
    description: str
    validation_criteria: List[Dict[str, Any]]
    severity: str


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
    compliance_level: ComplianceLevel
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    review_required: bool