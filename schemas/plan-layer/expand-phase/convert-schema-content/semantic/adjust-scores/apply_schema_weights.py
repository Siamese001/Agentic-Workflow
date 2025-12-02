"""
Schema definitions for schema weight application and adjustment.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class WeightingStrategy(Enum):
    """Weight application strategies."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    CUSTOM = "custom"


class WeightScope(Enum):
    """Scope of weight application."""
    GLOBAL = "global"
    LAYER_SPECIFIC = "layer_specific"
    ATTRIBUTE_LEVEL = "attribute_level"
    CONTEXT_DEPENDENT = "context_dependent"


@dataclass
class WeightConfiguration:
    """Schema for weight application configuration."""
    strategy: WeightingStrategy
    scope: WeightScope
    base_weights: Dict[str, float]
    adjustment_factors: Optional[Dict[str, float]] = None
    normalization_required: bool = True


@dataclass
class WeightedScore:
    """Schema for weighted score representation."""
    schema_id: str
    original_score: float
    applied_weight: float
    weighted_score: float
    weight_metadata: Dict[str, Any]


@dataclass
class WeightApplicationBatch:
    """Schema for batch weight application results."""
    batch_id: str
    weighted_scores: List[WeightedScore]
    configuration: WeightConfiguration
    application_statistics: Dict[str, float]