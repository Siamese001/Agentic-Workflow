"""Split module 2 for models_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

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

