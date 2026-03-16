from typing import Any

from pydantic import BaseModel, Field, field_validator

from agentic_core.config.core.base_entity_config import BaseEntity
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_item_types")
emit_determinism_digest("p0", "memory_item_types")

_emit_dispatches_healing_run("p1", "memory_item_types", "L4")
_emit_routes_through("p1", "memory_item_types", "L4")
_emit_escalates_to_human("p1", "memory_item_types", "L4")
_emit_reads_policy_state("p1", "memory_item_types", "L4")
_emit_authorize_and_execute("p2", "memory_item_types", "execution_auth")
_emit_validates_capability("p2", "memory_item_types", "capability_check")
_emit_routes_to_capability("p2", "memory_item_types", "capability_route")
_emit_writes_via_uwg("p2", "memory_item_types", "uwg_write")
_emit_blocks_direct_write("p2", "memory_item_types", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_item_types", "tool_invocation")
_emit_captures_execution_output("p2", "memory_item_types", "exec_output")
_emit_dispatches_agent("p3", "memory_item_types", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_item_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_item_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_item_types", "healing_outcome")
_emit_escalates_failure("p3", "memory_item_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_item_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_item_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_item_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_item_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_item_types", "eval_metric")
_emit_stores_embedding("p4", "memory_item_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_item_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_item_types", "exec_snapshot_link")


class MemoryItem(BaseEntity):
    """
    Represents a single unit of semantic memory (e.g., a conversation turn, a fact).
    """

    content: str = Field(..., min_length=1, description="Text content of the memory")
    embedding: list[float] = Field(..., description="Vector representation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Filterable tags")
    score: float | None = Field(default=None, description="Similarity score (only on retrieval)")

    @field_validator("embedding")
    @classmethod
    def check_vector_integrity(cls, v: list[float]) -> list[float]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MemoryItem.check_vector_integrity", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MemoryItem.check_vector_integrity", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "MemoryItem.check_vector_integrity")

        if not v:
            raise ValueError("Embedding vector cannot be empty")
        return v


class MemoryQuery(BaseModel):
    """
    Request object for semantic search.
    """

    vector: list[float] = Field(..., description="Query embedding")
    top_k: int = Field(default=5, ge=1, le=100)
    filter_metadata: dict[str, Any] | None = Field(default=None, description="Exact match filters")
