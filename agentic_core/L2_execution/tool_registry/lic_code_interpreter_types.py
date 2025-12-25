"""Types and models for lic_code_interpreter."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


@dataclass
class ScoredCandidate:
    """A scored candidate message."""

    _candidate_index: int
    _candidate_text: str
    _scores: Dict[str, float]
    _total_score: float


@dataclass
class ScoringCriteria:
    """Criteria for scoring candidates."""

    _strategic_alignment: float = 0.5
    _keyword_density: float = 0.3
    _readability: float = 0.2


@dataclass
class SimilarityResult:
    """Result of a similarity check."""

    _score: float
    _method: str
    _text1_length: int
    _text2_length: int


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""

    _keywords: List[str]
    _source_text_length: int
    _top_n: int
