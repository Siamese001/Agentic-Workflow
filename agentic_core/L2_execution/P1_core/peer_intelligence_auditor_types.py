"""Types and models for peer_intelligence_auditor."""
import logging

LOGGER = logging.getLogger(__name__)
class KeywordClassification(Enum):
    """TODO: Add docstring."""

    TABLE_STAKES = 'TABLE_STAKES'
    DIFFERENTIATOR = 'DIFFERENTIATOR'
    UNKNOWN = 'UNKNOWN'

@dataclass
class RAGHop:
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