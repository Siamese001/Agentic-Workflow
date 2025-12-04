"""
Schema definitions for memory ethics validation and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class EthicsDomain(Enum):
    """Memory ethics validation domains."""
    PRIVACY = "privacy"
    CONSENT = "consent"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"


class ComplianceLevel(Enum):
    """Ethics compliance levels."""
    STRICT = "strict"
    MODERATE = "moderate"
    BASIC = "basic"
    ADVISORY = "advisory"


@dataclass
class EthicsRule:
    """Schema for individual ethics rule."""
    rule_id: str
    domain: EthicsDomain
    compliance_level: ComplianceLevel
    rule_expression: str
    validation_criteria: Dict[str, Any]


@dataclass
class EthicsValidation:
    """Schema for ethics validation context."""
    validation_id: str
    target_memory_id: str
    rules_applied: List[EthicsRule]
    validation_timestamp: str
    validation_context: Dict[str, Any]


@dataclass
class EthicsValidationResult:
    """Schema for ethics validation results."""
    result_id: str
    validation: EthicsValidation
    ethics_passed: bool
    violations: List[Dict[str, Any]]
    recommendations: List[str]