"""
Schema definitions for schema score normalization and standardization.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class NormalizationTechnique(Enum):
    """Score normalization techniques."""
    MIN_MAX_SCALING = "min_max_scaling"
    Z_SCORE_NORMALIZATION = "z_score_normalization"
    RANK_NORMALIZATION = "rank_normalization"
    QUANTILE_NORMALIZATION = "quantile_normalization"


class ScoreDistribution(Enum):
    """Target score distribution types."""
    UNIFORM = "uniform"
    NORMAL = "normal"
    EXPONENTIAL = "exponential"
    CUSTOM = "custom"


@dataclass
class ScoreNormalizationConfig:
    """Schema for score normalization configuration."""
    technique: NormalizationTechnique
    target_range: Tuple[float, float]
    target_distribution: ScoreDistribution
    preserve_ordering: bool = True


@dataclass
class NormalizedScore:
    """Schema for normalized score representation."""
    original_schema_id: str
    original_score: float
    normalized_score: float
    normalization_metadata: Dict[str, Any]


@dataclass
class ScoreNormalizationBatch:
    """Schema for batch score normalization results."""
    batch_id: str
    normalized_scores: List[NormalizedScore]
    configuration: ScoreNormalizationConfig
    normalization_statistics: Dict[str, float]