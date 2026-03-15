from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "context_priority_types", "L4")
_emit_routes_through("p1", "context_priority_types", "L4")
_emit_escalates_to_human("p1", "context_priority_types", "L4")
_emit_reads_policy_state("p1", "context_priority_types", "L4")

"Types and models for ContextCurator."
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Priority levels for context chunks."""

    CRITICAL: Any = "critical"
    HIGH: Any = "high"
    MEDIUM: Any = "medium"
    LOW: Any = "low"


class ContextType(Enum):
    """Types of context chunks."""

    SYSTEM_INSTRUCTION: Any = "system_instruction"
    SAFETY_POLICY: Any = "SafetyPolicy"
    TASK_DESCRIPTION: Any = "task_description"
    CONVERSATION_HISTORY: Any = "conversation_history"
    RETRIEVED_KNOWLEDGE: Any = "retrieved_knowledge"
    TOOL_DOCUMENTATION: Any = "tool_documentation"
    EXAMPLE: Any = "example"


@dataclass
class ContextChunk:
    """Individual context chunk."""

    id: str
    content: str
    chunk_type: ContextType
    priority: ContextPriority
    token_count: int
    relevance_score: float = 0.0
    PINNED: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ContextChunk.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ContextChunk.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ContextChunk.to_dict")
        return {
            "id": self.id,
            "content": self.content,
            "chunk_type": self.chunk_type.value,
            "priority": self.priority.value,
            "token_count": self.token_count,
            "relevance_score": self.relevance_score,
            "pinned": self.pinned,
            "metadata": self.metadata,
        }


@dataclass
class ContextWindow:
    """Managed context window."""

    chunks: list[ContextChunk]
    total_tokens: int
    max_tokens: int
    pinned_tokens: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "total_tokens": self.total_tokens,
            "max_tokens": self.max_tokens,
            "pinned_tokens": self.pinned_tokens,
            "available_tokens": self.max_tokens - self.total_tokens,
        }
