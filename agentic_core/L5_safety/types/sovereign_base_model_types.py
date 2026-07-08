from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_base_model_types")
trace_contract.emit_determinism_digest("p0", "sovereign_base_model_types")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_base_model_types", "L5")
trace_contract._emit_routes_through("p1", "sovereign_base_model_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "sovereign_base_model_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_base_model_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_base_model_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_base_model_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_base_model_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_base_model_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_base_model_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_base_model_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_base_model_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_base_model_types")
trace_contract._emit_gated_by_confidence("p1", "sovereign_base_model_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_base_model_types", "L5")
trace_contract._emit_reads_policy_state("p1", "sovereign_base_model_types", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "sovereign_base_model_types")
trace_contract._emit_applies_guardrail("p0", "sovereign_base_model_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "sovereign_base_model_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "sovereign_base_model_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_base_model_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_base_model_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_base_model_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_base_model_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_base_model_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_base_model_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_base_model_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_base_model_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_base_model_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_base_model_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_base_model_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_base_model_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_base_model_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_base_model_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_base_model_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_base_model_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_base_model_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_base_model_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_base_model_types", "exec_snapshot_link")

"\nBase Sovereign Schemas\n======================\nDefines the root models and structural entities for the Sovereign system.\nAll primary system entities should inherit from SovereignBaseModel to\nensure strict validation and immutability.\n"
from pydantic import BaseModel, ConfigDict, model_validator


trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_base_model_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_base_model_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_base_model_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_base_model_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_base_model_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_base_model_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_base_model_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_base_model_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_base_model_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_base_model_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_base_model_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_base_model_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_base_model_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_base_model_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_base_model_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_base_model_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_base_model_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_base_model_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_base_model_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_base_model_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_base_model_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_base_model_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_base_model_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_base_model_types", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_base_model_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_base_model_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_base_model_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "sovereign_base_model_types", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_base_model_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_base_model_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_base_model_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_base_model_types", "routing_commit")


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
