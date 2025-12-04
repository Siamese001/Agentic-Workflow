"""
Schema definitions for schema vector normalization and standardization.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class NormalizationMethod(Enum):
    """Vector normalization methods."""
    MIN_MAX = "min_max"
    Z_SCORE = "z_score"
    UNIT_VECTOR = "unit_vector"
    ROBUST_SCALER = "robust_scaler"


class ScalingDirection(Enum):
    """Scaling direction for normalization."""
    FORWARD = "forward"
    REVERSE = "reverse"


@dataclass
class NormalizationParameters:
    """Schema for normalization parameters."""
    method: NormalizationMethod
    target_range: Optional[Tuple[float, float]] = None
    feature_wise: bool = False
    preserve_sparsity: bool = True


@dataclass
class NormalizedVector:
    """Schema for normalized vector representation."""
    original_schema_id: str
    normalized_values: List[float]
    normalization_metadata: Dict[str, Any]
    normalization_timestamp: str


@dataclass
class NormalizationBatch:
    """Schema for batch normalization results."""
    batch_id: str
    normalized_vectors: List[NormalizedVector]
    parameters: NormalizationParameters
    statistics: Dict[str, float]