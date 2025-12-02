"""
Schema definitions for schema similarity retrieval and comparison.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class SimilarityRetrievalMethod(Enum):
    """Similarity retrieval methods."""
    K_NEAREST = "k_nearest"
    RADIUS_SEARCH = "radius_search"
    THRESHOLD_FILTER = "threshold_filter"
    RANKED_LIST = "ranked_list"


class ComparisonDimension(Enum):
    """Similarity comparison dimensions."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"


@dataclass
class SimilarityRetrievalQuery:
    """Schema for similarity retrieval query."""
    query_id: str
    target_schema_id: str
    retrieval_method: SimilarityRetrievalMethod
    dimensions: List[ComparisonDimension]
    threshold: float = 0.7
    max_results: int = 10


@dataclass
class SimilarityMatch:
    """Schema for individual similarity match."""
    match_id: str
    schema_id: str
    similarity_score: float
    dimension_scores: Dict[ComparisonDimension, float]
    match_reasoning: Optional[str] = None


@dataclass
class SimilarityRetrievalResult:
    """Schema for similarity retrieval results."""
    retrieval_id: str
    query: SimilarityRetrievalQuery
    matches: List[SimilarityMatch]
    processing_time_ms: int
    total_candidates_evaluated: int