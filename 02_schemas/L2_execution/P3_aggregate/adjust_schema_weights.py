"""
Schema definitions for schema weight adjustment and optimization.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class WeightAdjustmentMethod(Enum):
    """Weight adjustment methods."""
    GRADIENT_BASED = "gradient_based"
    GENETIC_OPTIMIZATION = "genetic_optimization"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"


class AdjustmentFrequency(Enum):
    """Weight adjustment frequency."""
    STATIC = "static"
    DYNAMIC_PER_BATCH = "dynamic_per_batch"
    ADAPTIVE_PERFORMANCE = "adaptive_performance"
    USER_FEEDBACK_DRIVEN = "user_feedback_driven"


@dataclass
class WeightAdjustmentConfig:
    method: WeightAdjustmentMethod
    frequency: AdjustmentFrequency
    convergence_criteria: Dict[str, float]
    learning_rate: float = 0.01
    regularization_strength: float = 0.1
    """Schema for weight adjustment configuration."""


@dataclass
class WeightAdjustment:
    """Schema for individual weight adjustment."""
    adjustment_id: str
    original_weights: Dict[str, float]
    adjusted_weights: Dict[str, float]
    adjustment_reason: str
    performance_impact: float


@dataclass
class WeightAdjustmentHistory:
    """Schema for weight adjustment history tracking."""
    history_id: str
    adjustments: List[WeightAdjustment]
    configuration: WeightAdjustmentConfig
    performance_trend: List[float]