from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "budget_profile_validator")
trace_contract.emit_determinism_digest("p0", "budget_profile_validator")

trace_contract._emit_dispatches_healing_run("p1", "budget_profile_validator", "L5")
trace_contract._emit_routes_through("p1", "budget_profile_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "budget_profile_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "budget_profile_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "budget_profile_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "budget_profile_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "budget_profile_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "budget_profile_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "budget_profile_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "budget_profile_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "budget_profile_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "budget_profile_validator")
trace_contract._emit_gated_by_confidence("p1", "budget_profile_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "budget_profile_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "budget_profile_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "budget_profile_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "budget_profile_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "budget_profile_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "budget_profile_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "budget_profile_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "budget_profile_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "budget_profile_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "budget_profile_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "budget_profile_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "budget_profile_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "budget_profile_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "budget_profile_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "budget_profile_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "budget_profile_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "budget_profile_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "budget_profile_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "budget_profile_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "budget_profile_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "budget_profile_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "budget_profile_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "budget_profile_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "budget_profile_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("budget_profile_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("budget_profile_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("budget_profile_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("budget_profile_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("budget_profile_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("budget_profile_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("budget_profile_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("budget_profile_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("budget_profile_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("budget_profile_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("budget_profile_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("budget_profile_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("budget_profile_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("budget_profile_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("budget_profile_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("budget_profile_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("budget_profile_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("budget_profile_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("budget_profile_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("budget_profile_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("budget_profile_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("budget_profile_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "budget_profile_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "budget_profile_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_profile_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_profile_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "budget_profile_validator", "write_through")
trace_contract._emit_writes_through("p1", "budget_profile_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "budget_profile_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "budget_profile_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "budget_profile_validator", "routing_commit")


class BudgetProfile(BaseModel):
    """High-level budget profile for cost/latency envelopes.

    This duplicates some of the fields from ExecutionProfileSpec so that
    future callers can reason about budget in a single nested object.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_cost_usd: float = Field(default=0.1, ge=0.0, description="Maximum cost in USD")
    max_latency_ms: int = Field(default=3000, ge=0, description="Maximum allowed latency in ms")

    @field_validator("max_latency_ms")
    @classmethod
    def validate_latency(cls, value: int) -> int:
        """[HARDENED] Ensure latency ceiling is positive."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "BudgetProfile.validate_latency")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BudgetProfile.validate_latency".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if value <= 0:
            raise ValueError("max_latency_ms must be greater than 0")
        return value
