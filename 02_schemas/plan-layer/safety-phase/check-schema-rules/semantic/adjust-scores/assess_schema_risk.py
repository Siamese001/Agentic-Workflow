"""
Schema definitions for schema risk assessment and evaluation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RiskCategory(Enum):
    """Risk assessment categories."""
    SECURITY_RISK = "security_risk"
    PRIVACY_RISK = "privacy_risk"
    PERFORMANCE_RISK = "performance_risk"
    COMPLIANCE_RISK = "compliance_risk"
    OPERATIONAL_RISK = "operational_risk"


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


@dataclass
class RiskFactor:
    """Schema for individual risk factor."""
    factor_id: str
    category: RiskCategory
    description: str
    impact_score: float
    likelihood_score: float
    mitigation_suggestions: List[str]


@dataclass
class RiskAssessment:
    """Schema for risk assessment context."""
    assessment_id: str
    target_schema_id: str
    risk_factors: List[RiskFactor]
    assessment_timestamp: str
    assessment_context: Dict[str, Any]


@dataclass
class RiskAssessmentResult:
    """Schema for risk assessment results."""
    result_id: str
    assessment: RiskAssessment
    overall_risk_level: RiskLevel
    risk_score: float
    priority_actions: List[str]
    monitoring_required: bool
