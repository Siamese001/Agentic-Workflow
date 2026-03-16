from __future__ import annotations

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

emit_replay_key("p0", "sovereign_base_model_types")
emit_determinism_digest("p0", "sovereign_base_model_types")

_emit_dispatches_healing_run("p1", "sovereign_base_model_types", "L5")
_emit_routes_through("p1", "sovereign_base_model_types", "L5")
_emit_escalates_to_human("p1", "sovereign_base_model_types", "L5")
_emit_reads_policy_state("p1", "sovereign_base_model_types", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "sovereign_base_model_types")
_emit_applies_guardrail("p0", "sovereign_base_model_types", "p0_governance")
_emit_snapshots_state("p0", "sovereign_base_model_types", "state_snapshot")
_emit_authorize_and_execute("p2", "sovereign_base_model_types", "execution_auth")
_emit_validates_capability("p2", "sovereign_base_model_types", "capability_check")
_emit_routes_to_capability("p2", "sovereign_base_model_types", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_base_model_types", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_base_model_types", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_base_model_types", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_base_model_types", "exec_output")
_emit_dispatches_agent("p3", "sovereign_base_model_types", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_base_model_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_base_model_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_base_model_types", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_base_model_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_base_model_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_base_model_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_base_model_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_base_model_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_base_model_types", "eval_metric")
_emit_stores_embedding("p4", "sovereign_base_model_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_base_model_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_base_model_types", "exec_snapshot_link")

"\nBase Sovereign Schemas\n======================\nDefines the root models and structural entities for the Sovereign system.\nAll primary system entities should inherit from SovereignBaseModel to\nensure strict validation and immutability.\n"
from pydantic import BaseModel, ConfigDict, model_validator


class SovereignBaseModel(BaseModel):
    """
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    @model_validator(mode="after")
    def validate_invariants(self) -> SovereignBaseModel:
        """Cross-field validation hook for shared invariants."""
        return self


class Territory(SovereignBaseModel):
    """
    Represents a logical or physical boundary within the system.
    Used for mapping organizational depth and canonical paths.
    """

    name: str
    depth: int
    path: str
    canon_key: int | None = None
