"""
Schema definitions for schema result sorting and ordering.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum


class SortOrder(Enum):
    """Result sorting orders."""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    CUSTOM = "custom"


class SortCriterion(Enum):
    """Result sorting criteria."""
    SCORE = "score"
    TIMESTAMP = "timestamp"
    RELEVANCE = "relevance"
    CONFIDENCE = "confidence"
    ALPHABETICAL = "alphabetical"


@dataclass
class SortConfiguration:
    """Schema for sorting configuration."""
    primary_criterion: SortCriterion
    primary_order: SortOrder
    secondary_criteria: Optional[List[Tuple[SortCriterion, SortOrder]]] = None
    stable_sort: bool = True
    null_handling: str = "last"


@dataclass
class SortedResult:
    """Schema for individual sorted result."""
    result_id: str
    original_position: int
    sorted_position: int
    sort_key: Union[str, int, float]
    sort_metadata: Dict[str, Any]


@dataclass
class SortResult:
    """Schema for complete sort operation results."""
    sort_id: str
    sorted_results: List[SortedResult]
    configuration: SortConfiguration
    sort_statistics: Dict[str, Any]