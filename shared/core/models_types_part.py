"""Split module 1 for models_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class Provider(str, Enum):
    """Available LLM providers."""
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    MISTRAL = 'mistral'
    COHERE = 'cohere'
    GROQ = 'groq'
    TOGETHER = 'together'
    FIREWORKS = 'fireworks'

class APICallStatus(Enum):
    """Status of API calls."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()
    RATE_LIMITED = auto()

@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, object] = field(default_factory=dict)

@dataclass
class ThematicAnalysis:
    """Thematic analysis results from content inspection."""
    primary_theme: Dict[str, object] = field(default_factory=dict)
    secondary_themes: List[Dict[str, object]] = field(default_factory=list)
    role_classification: Dict[str, object] = field(default_factory=dict)
    positioning_directives: Dict[str, object] = field(default_factory=dict)
    authenticity_patterns: Dict[str, object] = field(default_factory=dict)
    competitive_intelligence: object = None
    problem_solution_narratives: Optional[Dict[str, object]] = None
    signal_quality_score: float = 0.0
    retrieval_method: str = 'UNKNOWN'
    retrieval_sources: List[Any] = field(default_factory=list)
    weighting_formula: Optional[Dict[str, object]] = None

@dataclass
class APICallMetrics:
    """Metrics for API call tracking"""
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0
    safety_blocks: int = 0
    rate_limits: int = 0

@dataclass
class RAGState:
    """State of RAG (Retrieval-Augmented Generation) process."""
    query: str = ''
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    context: str = ''
    response: str = ''
    retrieval_score: float = 0.0
    generation_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImmutableStagingBuffer:
    """Immutable buffer for staging data transformations."""
    data: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None

    def with_data(self, new_data: Dict[str, Any]) -> ImmutableStagingBuffer:
        """Return a new buffer with updated data."""
        return ImmutableStagingBuffer(data={**self.data, **new_data}, version=self.version + 1, timestamp=datetime.utcnow(), checksum=None)

    def clear(self) -> ImmutableStagingBuffer:
        """Return a new empty buffer."""
        return ImmutableStagingBuffer(version=self.version + 1, timestamp=datetime.utcnow())
