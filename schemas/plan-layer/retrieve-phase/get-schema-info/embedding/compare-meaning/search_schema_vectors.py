"""
Schema definitions for schema vector search and similarity operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class SearchMethod(Enum):
    """Vector search methods."""
    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    DOT_PRODUCT = "dot_product"
    APPROXIMATE_NEAREST = "approximate_nearest"


class SearchScope(Enum):
    """Vector search scopes."""
    FULL_VECTOR = "full_vector"
    PARTIAL_VECTOR = "partial_vector"
    WEIGHTED_VECTOR = "weighted_vector"
    SEGMENTED_VECTOR = "segmented_vector"


@dataclass
class VectorSearchQuery:
    """Schema for vector search query."""
    query_id: str
    query_vector: List[float]
    search_method: SearchMethod
    search_scope: SearchScope
    threshold: float = 0.8
    max_results: int = 10


@dataclass
class VectorSearchResult:
    """Schema for individual vector search result."""
    result_id: str
    schema_id: str
    similarity_score: float
    distance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VectorSearchResponse:
    """Schema for complete vector search response."""
    search_id: str
    query: VectorSearchQuery
    results: List[VectorSearchResult]
    search_time_ms: int
    total_candidates: int