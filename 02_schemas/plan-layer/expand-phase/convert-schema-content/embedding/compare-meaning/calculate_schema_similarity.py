"""
Schema definitions for schema similarity calculation and comparison.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SimilarityMetric(Enum):
    """Similarity calculation metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    PEARSON = "pearson"
    JACCARD = "jaccard"


class ComparisonScope(Enum):
    """Scope of schema comparison."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    ATTRIBUTE_LEVEL = "attribute_level"


@dataclass
class SimilarityConfiguration:
    """Schema for similarity calculation configuration."""
    metric: SimilarityMetric
    scope: ComparisonScope
    weight_semantic: float = 0.5
    weight_structural: float = 0.5
    threshold: float = 0.8


@dataclass
class SchemaComparison:
    """Schema for individual schema comparison."""
    schema_a_id: str
    schema_b_id: str
    similarity_score: float
    comparison_details: Dict[str, Any]
    comparison_timestamp: str


@dataclass
class SimilarityMatrix:
    """Schema for similarity matrix results."""
    matrix_id: str
    schema_ids: List[str]
    similarity_scores: List[List[float]]
    configuration: SimilarityConfiguration