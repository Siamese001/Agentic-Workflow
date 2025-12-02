"""
Schema definitions for orchestration-level schema confidence assessment.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ConfidenceSource(Enum):
    """Orchestration confidence sources."""
    HISTORICAL_DATA = "historical_data"
    PEER_FEEDBACK = "peer_feedback"
    AUTOMATED_METRICS = "automated_metrics"
    EXPERT_EVALUATION = "expert_evaluation"


class AssessmentMethod(Enum):
    """Confidence assessment methods."""
    STATISTICAL = "statistical"
    HEURISTIC = "heuristic"
    BAYESIAN = "bayesian"
    ENSEMBLE = "ensemble"


@dataclass
class ConfidenceAssessmentConfig:
    """Schema for confidence assessment configuration."""
    sources: List[ConfidenceSource]
    assessment_method: AssessmentMethod
    confidence_threshold: float = 0.8
    include_uncertainty: bool = True


@dataclass
class ConfidenceAssessmentResult:
    """Schema for confidence assessment results."""
    assessment_id: str
    configuration: ConfidenceAssessmentConfig
    overall_confidence: float
    source_contributions: Dict[ConfidenceSource, float]
    uncertainty_estimate: Optional[float]
    assessment_timestamp: str
