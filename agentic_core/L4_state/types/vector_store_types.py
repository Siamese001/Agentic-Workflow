from abc import ABC, abstractmethod

from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "vector_store_types")
emit_determinism_digest("p0", "vector_store_types")

_emit_dispatches_healing_run("p1", "vector_store_types", "L4")
_emit_routes_through("p1", "vector_store_types", "L4")
_emit_escalates_to_human("p1", "vector_store_types", "L4")
_emit_reads_policy_state("p1", "vector_store_types", "L4")

_emit_snapshots_state("p0", "vector_store_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "vector_store_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "vector_store_types")
_emit_authorize_and_execute("p2", "vector_store_types", "execution_auth")
_emit_validates_capability("p2", "vector_store_types", "capability_check")
_emit_routes_to_capability("p2", "vector_store_types", "capability_route")
_emit_writes_via_uwg("p2", "vector_store_types", "uwg_write")
_emit_blocks_direct_write("p2", "vector_store_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vector_store_types", "tool_invocation")
_emit_captures_execution_output("p2", "vector_store_types", "exec_output")
_emit_dispatches_agent("p3", "vector_store_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vector_store_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vector_store_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vector_store_types", "healing_outcome")
_emit_escalates_failure("p3", "vector_store_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vector_store_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vector_store_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vector_store_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vector_store_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vector_store_types", "eval_metric")
_emit_stores_embedding("p4", "vector_store_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vector_store_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vector_store_types", "exec_snapshot_link")


class BaseVectorStore(ABC):
    """
    Interface for vector database interactions.
    All methods must be Async to support high-throughput IO.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Perform any connection handshakes or schema setups."""
        pass

    @abstractmethod
    async def upsert(self, items: list[MemoryItem]) -> bool:
        """Insert or Update memory items."""
        pass

    @abstractmethod
    async def query(self, query: MemoryQuery) -> list[MemoryItem]:
        """Retrieve nearest neighbors."""
        pass

    @abstractmethod
    async def delete(self, item_ids: list[str]) -> bool:
        """Remove items by ID."""
        pass
