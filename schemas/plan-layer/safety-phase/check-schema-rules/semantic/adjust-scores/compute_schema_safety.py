"""
Schema definitions for schema safety computation and scoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from enum import Enum


class SafetyMetric(Enum):
    """Safety computation metrics."""
    VULNERABILITY_SCORE = "vulnerability_score"
    THREAT_LEVEL = "threat_level"
    EXPOSURE_RISK = "exposure_risk"
    CONTAINMENT_EFFECTIVENESS = "containment_effectiveness"


class ComputationMethod(Enum):
    """Safety computation methods."""
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    HYBRID = "hybrid"
    BAYESIAN = "bayesian"


@dataclass
class SafetyComputationConfig:
    """Schema for safety computation configuration."""
    method: ComputationMethod
    metrics: List[SafetyMetric]
    weight_scheme: Dict[SafetyMetric, float]
    confidence_threshold: float = 0.8
    include_uncertainty: bool = True


@dataclass
class SafetyScore:
    """Schema for individual safety score."""
    metric: SafetyMetric
    score: float
    contributing_factors: List[str]
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class SafetyComputationResult:
    """Schema for safety computation results."""
    computation_id: str
    target_schema_id: str
    overall_safety_score: float
    metric_scores: List[SafetyScore]
    configuration: SafetyComputationConfig
    computation_timestamp: str
