"""
Schema definitions for schema confidence computation and scoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class ConfidenceMetric(Enum):
    """Confidence computation metrics."""
    STATISTICAL = "statistical"
    HEURISTIC = "heuristic"
    ENSEMBLE = "ensemble"
    BAYESIAN = "bayesian"


class ConfidenceLevel(Enum):
    """Confidence level classifications."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ConfidenceConfiguration:
    """Schema for confidence computation configuration."""
    metric: ConfidenceMetric
    threshold_levels: Dict[ConfidenceLevel, float]
    include_uncertainty: bool = True
    confidence_interval: float = 0.95


@dataclass
class ConfidenceScore:
    """Schema for confidence score representation."""
    schema_id: str
    confidence_value: float
    confidence_level: ConfidenceLevel
    uncertainty_estimate: Optional[float] = None
    contributing_factors: Optional[List[str]] = None


@dataclass
class ConfidenceComputationBatch:
    """Schema for batch confidence computation results."""
    batch_id: str
    confidence_scores: List[ConfidenceScore]
    configuration: ConfidenceConfiguration
    computation_statistics: Dict[str, float]