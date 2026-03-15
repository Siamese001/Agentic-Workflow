from __future__ import annotations

"\nIRagProvider - Unified RAG Interface for L0-L6 Architecture\nDefines standard contract for all RAG implementations\n"
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


@dataclass
class RagQuery:
    """Standard RAG query input."""

    query: str
    top_k: int = 10
    filters: dict[str, Any] = field(default_factory=dict)
    namespace: str = "sovereign-core"
    enable_reranking: bool = True
    enable_caching: bool = True
    mission_context: dict[str, Any] | None = None


@dataclass
class RagDocument:
    """Standard RAG document output."""

    id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"


@dataclass
class RagResult:
    """Standard RAG result with telemetry."""

    query: str
    documents: list[RagDocument]
    latency_ms: float
    cached: bool = False
    reranked: bool = False
    faithfulness_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class IRagProvider(ABC):
    """
    Unified RAG Provider Interface.

    All RAG implementations (L1, L3, L4, L5, apps_shared) must implement this.
    """

    @abstractmethod
    async def retrieve(self, query: RagQuery) -> RagResult:
        """
        Retrieve documents for a query.

        Args:
            query: Structured RAG query

        Returns:
            RagResult with documents and telemetry
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "IRagProvider.retrieve", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "IRagProvider.retrieve", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "IRagProvider.retrieve")
        pass

    @abstractmethod
    async def index(self, documents: list[RagDocument], namespace: str = "sovereign-core") -> dict[str, int]:
        """
        Index documents into RAG system.

        Args:
            documents: Documents to index
            namespace: Namespace for isolation

        Returns:
            Stats: {indexed: int, failed: int, skipped: int}
        """
        pass

    @abstractmethod
    def get_health(self) -> dict[str, Any]:
        """Get RAG system health status."""
        pass


__all__ = ["IRagProvider", "RagQuery", "RagDocument", "RagResult"]
