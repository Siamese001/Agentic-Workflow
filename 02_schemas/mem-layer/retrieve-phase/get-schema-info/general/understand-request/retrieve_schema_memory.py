"""
Schema definitions for memory-based schema retrieval operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class MemoryType(Enum):
    """Types of memory storage for schemas."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"
    LONG_TERM = "long_term"


class RetrievalStrategy(Enum):
    """Memory retrieval strategies."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    TEMPORAL_PROXIMITY = "temporal_proximity"
    ASSOCIATIVE = "associative"


@dataclass
class MemoryQuery:
    """Schema for memory query parameters."""
    query_type: MemoryType
    strategy: RetrievalStrategy
    search_terms: List[str]
    filters: Optional[Dict[str, Any]] = None
    max_results: int = 10


@dataclass
class MemoryEntry:
    """Schema for individual memory entry."""
    entry_id: str
    content: Dict[str, Any]
    timestamp: str
    relevance_score: float
    metadata: Optional[Dict[str, str]] = None


@dataclass
class MemoryRetrievalResult:
    """Schema for memory retrieval results."""
    query_id: str
    entries: List[MemoryEntry]
    total_found: int
    retrieval_time_ms: int