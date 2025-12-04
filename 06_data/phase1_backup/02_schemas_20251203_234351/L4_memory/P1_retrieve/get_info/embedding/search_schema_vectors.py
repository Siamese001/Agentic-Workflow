"""
Schema definitions for schema vector search and similarity operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from enum import Enum


class SearchMethod(Enum):
    """Schema vector search methods."""
    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    DOT_PRODUCT = "dot_product"
    MANHATTAN_DISTANCE = "manhattan_distance"


class SearchScope(Enum):
    """Vector search scopes."""
    LOCAL = "local"
    GLOBAL = "global"
    DOMAIN_SPECIFIC = "domain_specific"
    CROSS_DOMAIN = "cross_domain"


@dataclass
class VectorSearchQuery:
    """Schema for vector search query."""
    query_id: str
    query_vector: List[float]
    search_method: SearchMethod
    search_scope: SearchScope
    similarity_threshold: float = 0.8


@dataclass
class VectorSearch:
    """Schema for vector search operation."""
    search_id: str
    query: VectorSearchQuery
    target_vectors: List[List[float]]
    search_timestamp: str
    search_parameters: Dict[str, Any]


@dataclass
class VectorSearchResult:
    """Schema for vector search results."""
    result_id: str
    search: VectorSearch
    similar_vectors: List[Tuple[str, float]]
    search_successful: bool
    search_metadata: Dict[str, Any]