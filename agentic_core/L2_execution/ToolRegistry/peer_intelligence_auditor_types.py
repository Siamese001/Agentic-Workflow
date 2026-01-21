from __future__ import annotations

"""Types and models for PeerIntelligenceAuditorAgent."""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

Logger: Any = logging.getLogger(__name__)

class KeywordClassification(Enum):
    """TODO: Add docstring."""
    TABLE_STAKES: Any = 'TABLE_STAKES'
    DIFFERENTIATOR: Any = 'DIFFERENTIATOR'
    UNKNOWN: Any = 'UNKNOWN'

@dataclass
class RagHop:
    """Docstring."""
    hop_number: int
    search_queries: list[str]
    results: list[dict[str, Any]]
    keywords_found: set[str]

@dataclass
class KeywordAnalysis:
    """Docstring."""
    keyword: str
    classification: KeywordClassification
    frequency_score: float
    competitive_density: float
    reasoning: str

@dataclass
class PeerIntelligenceConfig:
    """Docstring."""
    total_searches: int = 24
    total_hops: int = 3
    searches_per_hop: int = 8
    differentiator_threshold: float = 0.3

@dataclass
class PeerIntelligenceResult:
    """Docstring."""
    hops: list[RAGHop]
    keyword_analyses: list[KeywordAnalysis]
    table_stakes: list[str]
    differentiators: list[str]
    validation_results: list[ValidationResult]
    success: bool
    total_searches_executed: int
