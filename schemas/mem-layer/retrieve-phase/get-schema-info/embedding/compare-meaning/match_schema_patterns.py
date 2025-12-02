"""
Schema definitions for schema pattern matching and recognition.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from enum import Enum


class PatternType(Enum):
    """Schema pattern types."""
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"


class MatchingStrategy(Enum):
    """Pattern matching strategies."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    PARTIAL = "partial"
    APPROXIMATE = "approximate"


@dataclass
class SchemaPattern:
    """Schema for individual schema pattern."""
    pattern_id: str
    pattern_type: PatternType
    pattern_definition: Dict[str, Any]
    matching_criteria: Dict[str, Any]


@dataclass
class PatternMatching:
    """Schema for pattern matching context."""
    matching_id: str
    target_schema_id: str
    patterns_to_match: List[SchemaPattern]
    matching_strategy: MatchingStrategy
    matching_timestamp: str


@dataclass
class PatternMatchingResult:
    """Schema for pattern matching results."""
    result_id: str
    matching: PatternMatching
    matched_patterns: List[Dict[str, Any]]
    match_scores: List[Tuple[str, float]]
    matching_successful: bool