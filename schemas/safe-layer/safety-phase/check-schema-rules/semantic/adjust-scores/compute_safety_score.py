"""
Schema definitions for safety score computation and analysis.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ScoreMetric(Enum):
    """Safety score computation metrics."""
    VULNERABILITY = "vulnerability"
    THREAT_LEVEL = "threat_level"
    EXPOSURE = "exposure"
    CONTAINMENT = "containment"


class ComputationMethod(Enum):
    """Safety score computation methods."""
    WEIGHTED_AVERAGE = "weighted_average"
    BAYESIAN = "bayesian"
    STATISTICAL = "statistical"
    HEURISTIC = "heuristic"


@dataclass
class ScoreComponent:
    """Schema for individual score component."""
    component_id: str
    metric: ScoreMetric
    value: float
    weight: float
    confidence: float


@dataclass
class SafetyScoreComputation:
    """Schema for safety score computation."""
    computation_id: str
    target_schema_id: str
    computation_method: ComputationMethod
    components: List[ScoreComponent]
    computation_timestamp: str


@dataclass
class SafetyScoreResult:
    """Schema for safety score computation results."""
    result_id: str
    computation: SafetyScoreComputation
    overall_score: float
    confidence_level: float
    risk_classification: str