"""Types and models for lic_code_interpreter."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class ScoredCandidate:
    """A scored candidate message."""
    candidate_index: int
    candidate_text: str
    scores: Dict[str, float]
    total_score: float

@dataclass
class ScoringCriteria:
    """Criteria for scoring candidates."""
    strategic_alignment: float = 0.5
    keyword_density: float = 0.3
    readability: float = 0.2

@dataclass
class SimilarityResult:
    """Result of a similarity check."""
    score: float
    method: str
    text1_length: int
    text2_length: int

@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""
    keywords: List[str]
    source_text_length: int
    top_n: int

