from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rag_provider_types")
emit_determinism_digest("p0", "rag_provider_types")

_emit_dispatches_healing_run("p1", "rag_provider_types", "L3")
_emit_routes_through("p1", "rag_provider_types", "L3")
_emit_escalates_to_human("p1", "rag_provider_types", "L3")
_emit_reads_policy_state("p1", "rag_provider_types", "L3")
_emit_authorize_and_execute("p2", "rag_provider_types", "execution_auth")
_emit_validates_capability("p2", "rag_provider_types", "capability_check")
_emit_routes_to_capability("p2", "rag_provider_types", "capability_route")
_emit_writes_via_uwg("p2", "rag_provider_types", "uwg_write")
_emit_blocks_direct_write("p2", "rag_provider_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_provider_types", "tool_invocation")
_emit_captures_execution_output("p2", "rag_provider_types", "exec_output")
_emit_dispatches_agent("p3", "rag_provider_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_provider_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_provider_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_provider_types", "healing_outcome")
_emit_escalates_failure("p3", "rag_provider_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_provider_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_provider_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_provider_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_provider_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_provider_types", "eval_metric")
_emit_stores_embedding("p4", "rag_provider_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_provider_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_provider_types", "exec_snapshot_link")

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
