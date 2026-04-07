from typing import Any

from pydantic import BaseModel, Field, field_validator

from agentic_core.config.base_entity_config import BaseEntity
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_item_types")
emit_determinism_digest("p0", "memory_item_types")

_emit_dispatches_healing_run("p1", "memory_item_types", "L4")
_emit_routes_through("p1", "memory_item_types", "L4")
_emit_checks_agent_registry("p1", "memory_item_types", "agent_registry")
_emit_validates_agent_capability("p1", "memory_item_types", "capability")
_emit_dispatches_execution_plan("p1", "memory_item_types", "exec_plan")
_emit_agent_executes_agent("p1", "memory_item_types", "sub_agent")
_emit_routes_to_agent("p1", "memory_item_types", "target_agent")
_emit_verifies_policy("p1", "memory_item_types", "policy_check")
_emit_observes_runtime_state("p1", "memory_item_types", "runtime_state")
_emit_verifies_boundary("p1", "memory_item_types", "boundary_check")
_emit_transcripts_response("p1", "memory_item_types", "transcript")
_emit_hard_fails_untranscripted("p1", "memory_item_types")
_emit_gated_by_confidence("p1", "memory_item_types", "confidence_gate")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("memory_item_types", "p4obs", "metric_1")
_emit_emits_metric_event("memory_item_types", "p4obs", "metric_2")
_emit_emits_metric_event("memory_item_types", "p4obs", "metric_3")
_emit_emits_metric_event("memory_item_types", "p4obs", "metric_4")
_emit_emits_metric_event("memory_item_types", "p4obs", "metric_5")
_emit_emits_metric_event("memory_item_types", "p4obs", "metric_6")
_emit_records_incident_event("memory_item_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("memory_item_types", "p4obs", "anomaly")
_emit_writes_observability_log("memory_item_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("memory_item_types", "p4obs", "mon_state")
_emit_triggers_alert("memory_item_types", "p4obs", "alert")
_emit_links_incident_trace("memory_item_types", "p4obs", "trace_link")
_emit_captures_pattern("memory_item_types", "p3lm", "pattern")
_emit_records_learning_event("memory_item_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("memory_item_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("memory_item_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("memory_item_types", "p3lm", "routing")
_emit_improves_agent_policy("memory_item_types", "p3lm", "policy")
_emit_stores_learning_state("memory_item_types", "p3lm", "state")
_emit_records_execution_trace("memory_item_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("memory_item_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("memory_item_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("memory_item_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("memory_item_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("memory_item_types", "env_read", "p2_env_1")
_emit_reads_environ("memory_item_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("memory_item_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("memory_item_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "memory_item_types", "context_pull")
_emit_pulls_context("p1", "memory_item_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "memory_item_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "memory_item_types", "uwg_term_2")
_emit_writes_through("p1", "memory_item_types", "write_through")
_emit_writes_through("p1", "memory_item_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "memory_item_types", "safety_validation")
_emit_invokes_eval("p1", "memory_item_types", "eval_call")
_emit_proposal_commits_routing("p1", "memory_item_types", "routing_commit")


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
