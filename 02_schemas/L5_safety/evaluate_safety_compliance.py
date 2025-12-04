"""
Schema definitions for safety compliance evaluation and assessment.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ComplianceDomain(Enum):
    """Safety compliance evaluation domains."""
    REGULATORY = "regulatory"
    INDUSTRY = "industry"
    ORGANIZATIONAL = "organizational"
    TECHNICAL = "technical"


class EvaluationStatus(Enum):
    """Compliance evaluation status."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"


@dataclass
class ComplianceRequirement:
    """Schema for individual compliance requirement."""
    requirement_id: str
    domain: ComplianceDomain
    description: str
    criteria: Dict[str, Any]
    mandatory: bool = True


@dataclass
class ComplianceEvaluation:
    """Schema for compliance evaluation context."""
    evaluation_id: str
    target_schema_id: str
    requirements: List[ComplianceRequirement]
    evaluation_timestamp: str
    evaluation_context: Dict[str, Any]


@dataclass
class ComplianceEvaluationResult:
    """Schema for compliance evaluation results."""
    result_id: str
    evaluation: ComplianceEvaluation
    overall_status: EvaluationStatus
    compliance_score: float
    violations: List[Dict[str, Any]]