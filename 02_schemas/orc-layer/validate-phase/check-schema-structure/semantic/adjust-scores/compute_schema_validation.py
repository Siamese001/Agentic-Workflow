"""
Schema definitions for orchestration-level schema validation computation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class ValidationMetric(Enum):
    """Orchestration validation metrics."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    PERFORMANCE = "performance"


class ComputationStrategy(Enum):
    """Validation computation strategies."""
    AGGREGATE = "aggregate"
    WEIGHTED_AVERAGE = "weighted_average"
    BAYESIAN = "bayesian"
    ENSEMBLE = "ensemble"


@dataclass
class ValidationComputationConfig:
    """Schema for validation computation configuration."""
    metrics: List[ValidationMetric]
    computation_strategy: ComputationStrategy
    weight_scheme: Dict[ValidationMetric, float]
    confidence_threshold: float = 0.8


@dataclass
class ValidationComputationResult:
    """Schema for validation computation results."""
    computation_id: str
    configuration: ValidationComputationConfig
    overall_score: float
    metric_scores: Dict[ValidationMetric, float]
    confidence_level: float
    computation_timestamp: str
