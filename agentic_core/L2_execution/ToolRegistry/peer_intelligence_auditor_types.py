from __future__ import annotations
"""Types and models for PeerIntelligenceAuditorAgent."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Set
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
    search_queries: List[str]
    results: List[Dict[str, Any]]
    keywords_found: Set[str]

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
    hops: List[RAGHop]
    keyword_analyses: List[KeywordAnalysis]
    table_stakes: List[str]
    differentiators: List[str]
    validation_results: List[ValidationResult]
    success: bool
    total_searches_executed: int
