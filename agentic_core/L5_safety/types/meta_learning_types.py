"""
Meta-Learning Protocol for recall-or-execute pattern.

This protocol enables agents to cache and recall successful execution
patterns, improving performance and consistency over time.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "meta_learning_types", "L5")
_emit_routes_through("p1", "meta_learning_types", "L5")
_emit_escalates_to_human("p1", "meta_learning_types", "L5")
_emit_reads_policy_state("p1", "meta_learning_types", "L5")


@dataclass
class LearningContext:
    """Context for meta-learning operations."""

    context_key: str
    agent_name: str
    operation_type: str
    input_hash: str
    metadata: dict[str, Any] | None = field(default_factory=dict)

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
    cache_key: str | None = None
    execution_time_ms: float | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

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
    def recall_or_execute(self, context: LearningContext, execution_fn: Callable[[], Any]) -> LearningResult:
        """Recall from cache or execute and learn.

        Args:
            context: Learning context with cache key info
            execution_fn: Function to execute if cache miss

        Returns:
            LearningResult with result and cache status
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MetaLearningProtocol.recall_or_execute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MetaLearningProtocol.recall_or_execute", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_SAFETY, "MetaLearningProtocol.recall_or_execute"
        )
        pass

    @abstractmethod
    def learn_experience(self, context: LearningContext, result: Any, success: bool) -> bool:
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
    def invalidate_cache(self, context_key: str | None = None, agent_name: str | None = None) -> int:
        """Invalidate cached learnings.

        Args:
            context_key: Specific key to invalidate (None for all)
            agent_name: Invalidate all for specific agent

        Returns:
            Number of entries invalidated
        """
        pass

    @abstractmethod
    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if meta-learning system is available."""
        pass
