"""
Schema definitions for schema context matching and alignment.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class MatchingStrategy(Enum):
    """Context matching strategies."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_MATCH = "semantic_match"
    STRUCTURAL_MATCH = "structural_match"
    HYBRID_MATCH = "hybrid_match"


class MatchScope(Enum):
    """Context matching scopes."""
    FULL_CONTEXT = "full_context"
    PARTIAL_CONTEXT = "partial_context"
    KEY_ELEMENTS = "key_elements"
    RELATIONSHIPS_ONLY = "relationships_only"


@dataclass
class ContextMatchingConfig:
    """Schema for context matching configuration."""
    strategy: MatchingStrategy
    scope: MatchScope
    similarity_threshold: float = 0.7
    include_metadata: bool = True
    max_matches: int = 5


@dataclass
class ContextMatch:
    """Schema for individual context match."""
    match_id: str
    source_context_id: str
    target_context_id: str
    match_score: float
    match_type: str
    alignment_details: Dict[str, Any]


@dataclass
class ContextMatchingResult:
    """Schema for context matching results."""
    matching_id: str
    configuration: ContextMatchingConfig
    matches: List[ContextMatch]
    processing_time_ms: int
    total_contexts_analyzed: int