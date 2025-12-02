"""
Schema definitions for schema confidence assessment and evaluation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class ConfidenceFactor(Enum):
    """Factors affecting schema confidence."""
    DATA_QUALITY = "data_quality"
    MODEL_ACCURACY = "model_accuracy"
    HISTORICAL_PERFORMANCE = "historical_performance"
    EXPERT_VALIDATION = "expert_validation"
    PEER_REVIEW = "peer_review"


class AssessmentMethod(Enum):
    """Confidence assessment methods."""
    STATISTICAL_ANALYSIS = "statistical_analysis"
    EXPERT_EVALUATION = "expert_evaluation"
    CROSS_VALIDATION = "cross_validation"
    BENCHMARK_COMPARISON = "benchmark_comparison"


@dataclass
class ConfidenceAssessment:
    """Schema for confidence assessment configuration."""
    assessment_id: str
    method: AssessmentMethod
    factors_considered: List[ConfidenceFactor]
    weighting_scheme: Dict[ConfidenceFactor, float]
    confidence_level: str


@dataclass
class ConfidenceFactorScore:
    """Schema for individual confidence factor score."""
    factor: ConfidenceFactor
    score: float
    evidence: Optional[Dict[str, Any]] = None
    uncertainty: Optional[float] = None


@dataclass
class ConfidenceAssessmentResult:
    """Schema for confidence assessment results."""
    schema_id: str
    overall_confidence: float
    factor_scores: List[ConfidenceFactorScore]
    assessment_metadata: Dict[str, Any]
    assessment_timestamp: str