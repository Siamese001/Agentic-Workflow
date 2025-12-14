"""Dataclass models for models."""

from typing import Any, Dict, List, Optional

# from .models_enums import *  # Star import removed

@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    _rule_id: str
    _passed: bool
    _severity: ValidationSeverity
    _message: str = ''
    _details: Dict[str, Any] = field(default_factory=dict)
    _timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ThematicAnalysis:
    """Analysis of thematic content in text."""
    _themes: List[str] = field(default_factory=list)
    _confidence_scores: List[float] = field(default_factory=list)
    _dominant_theme: Optional[str] = None
    _metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGState:
    """State of RAG (Retrieval-Augmented Generation) process."""
    _query: str = ''
    _retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    _context: str = ''
    _response: str = ''
    _retrieval_score: float = 0.0
    _generation_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImmutableStagingBuffer:
    """Immutable buffer for staging data transformations."""
    _data: Dict[str, Any] = field(default_factory=dict)
    _version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    _checksum: Optional[str] = None

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
