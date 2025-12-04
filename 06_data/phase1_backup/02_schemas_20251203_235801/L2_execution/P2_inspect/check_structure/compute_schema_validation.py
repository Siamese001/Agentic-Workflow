"""
Schema definitions for schema validation computation and scoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class ValidationMetric(Enum):
    """Schema validation metrics."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    COVERAGE = "coverage"


class ComputationMethod(Enum):
    """Validation computation methods."""
    STATISTICAL = "statistical"
    HEURISTIC = "heuristic"
    MACHINE_LEARNING = "machine_learning"
    RULE_BASED = "rule_based"


@dataclass
class ValidationComputationConfig:
    """Schema for validation computation configuration."""
    method: ComputationMethod
    metrics: List[ValidationMetric]
    weight_scheme: Dict[ValidationMetric, float]
    confidence_threshold: float = 0.8


@dataclass
class ValidationScore:
    """Schema for individual validation score."""
    metric: ValidationMetric
    score: float
    confidence_interval: Tuple[float, float]
    supporting_data: Optional[Dict[str, Any]] = None


@dataclass
class ValidationComputationResult:
    """Schema for validation computation results."""
    validation_id: str
    schema_id: str
    overall_score: float
    metric_scores: List[ValidationScore]
    computation_metadata: Dict[str, Any]
    computation_timestamp: str