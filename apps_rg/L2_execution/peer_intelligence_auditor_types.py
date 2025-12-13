"""Types and models for peer_intelligence_auditor."""

from enum import Enum

class KeywordClassification(Enum):
    """TODO: Add docstring."""

    TABLE_STAKES = 'TABLE_STAKES'
    DIFFERENTIATOR = 'DIFFERENTIATOR'
    UNKNOWN = 'UNKNOWN'

@dataclass
    """TODO: Add docstring."""

class RAGHop:
    hop_number: int
    search_queries: List[str]
    results: List[Dict[str, Any]]
    keywords_found: Set[str]

    """TODO: Add docstring."""

@dataclass
class KeywordAnalysis:
    keyword: str
    classification: KeywordClassification
    frequency_score: float
    competitive_density: float
    reasoning: str
    """TODO: Add docstring."""


@dataclass
class PeerIntelligenceConfig:
    total_searches: int = 24
    total_hops: int = 3
    searches_per_hop: int = 8
    """TODO: Add docstring."""

    differentiator_threshold: float = 0.3

@dataclass
class PeerIntelligenceResult:
    hops: List[RAGHop]
    keyword_analyses: List[KeywordAnalysis]
    table_stakes: List[str]
    differentiators: List[str]
    validation_results: List[ValidationResult]
    success: bool
    total_searches_executed: int
