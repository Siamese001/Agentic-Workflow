"""Dataclass models for models."""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
# from .models_enums import *  # Star import removed

@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str = ''
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ThematicAnalysis:
    """Analysis of thematic content in text."""
    themes: List[str] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    dominant_theme: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

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
        return ImmutableStagingBuffer(data={**self.data,
            **new_data},
            version=self.version + 1,
            timestamp=datetime.utcnow(),
            checksum=None)

    def clear(self) -> ImmutableStagingBuffer:
        """Return a new empty buffer."""
        return ImmutableStagingBuffer(version=self.version + 1, timestamp=datetime.utcnow())
