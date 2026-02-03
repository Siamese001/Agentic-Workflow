"""
Meta-Learning Protocol for recall-or-execute pattern.

This protocol enables agents to cache and recall successful execution
patterns, improving performance and consistency over time.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class LearningContext:
    """Context for meta-learning operations."""

    context_key: str
    agent_name: str
    operation_type: str
    input_hash: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    def to_cache_key(self) -> str:
        """Generate cache key from context."""
        return f"{self.agent_name}:{self.operation_type}:{self.input_hash}"


@dataclass
class LearningResult:
    """Result of meta-learning operation."""

    success: bool
    from_cache: bool
    result: Any
    confidence: float = 1.0
    cache_key: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class MetaLearningProtocol(ABC):
    """Protocol for meta-learning implementations.

    Implementations must provide recall-or-execute pattern:
    1. Check cache for previous successful execution
    2. If found and confident, return cached result
    3. If not found, execute and cache successful results
    """

    @abstractmethod
    def recall_or_execute(
        self,
        context: LearningContext,
        execution_fn: Callable[[], Any],
    ) -> LearningResult:
        """Recall from cache or execute and learn.

        Args:
            context: Learning context with cache key info
            execution_fn: Function to execute if cache miss

        Returns:
            LearningResult with result and cache status
        """
        pass

    @abstractmethod
    def learn_experience(
        self,
        context: LearningContext,
        result: Any,
        success: bool,
    ) -> bool:
        """Store learning experience for future recall.

        Args:
            context: Learning context
            result: Result to cache
            success: Whether execution was successful

        Returns:
            True if learning was stored successfully
        """
        pass

    @abstractmethod
    def invalidate_cache(
        self,
        context_key: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> int:
        """Invalidate cached learnings.

        Args:
            context_key: Specific key to invalidate (None for all)
            agent_name: Invalidate all for specific agent

        Returns:
            Number of entries invalidated
        """
        pass

    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if meta-learning system is available."""
        pass
