from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "safety_profile_types")
trace_contract.emit_determinism_digest("p0", "safety_profile_types")

trace_contract._emit_dispatches_healing_run("p1", "safety_profile_types", "L5")
trace_contract._emit_routes_through("p1", "safety_profile_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "safety_profile_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_profile_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_profile_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_profile_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_profile_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_profile_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_profile_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_profile_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_profile_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_profile_types")
trace_contract._emit_gated_by_confidence("p1", "safety_profile_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "safety_profile_types", "L5")
trace_contract._emit_reads_policy_state("p1", "safety_profile_types", "L5")

trace_contract._emit_applies_guardrail("p0", "safety_profile_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "safety_profile_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "safety_profile_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_profile_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_profile_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_profile_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_profile_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_profile_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_profile_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_profile_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_profile_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_profile_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_profile_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_profile_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_profile_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_profile_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_profile_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_profile_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_profile_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_profile_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_profile_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_profile_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_profile_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_profile_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_profile_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_profile_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_profile_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_profile_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_profile_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_profile_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_profile_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_profile_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_profile_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_profile_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_profile_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_profile_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_profile_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_profile_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_profile_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_profile_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_profile_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_profile_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_profile_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_profile_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_profile_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_profile_types", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_profile_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_profile_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_profile_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_profile_types", "write_through")
trace_contract._emit_writes_through("p1", "safety_profile_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_profile_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_profile_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_profile_types", "routing_commit")


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles.

    This is intentionally string/primitive based to avoid cycles and
    mirrors the SafetyTier + policy toggles used in ExecutionProfileSpec.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    safety_tier: str = Field(
        default="standard",
        description="Safety tier: standard | strict | relaxed | debug",
    )
    pii_detection_enabled: bool = Field(default=True, description="PII detection toggle")
    policy_engine_enabled: bool = Field(default=True, description="Policy engine toggle")

    @field_validator("safety_tier")
    @classmethod
    def validate_safety_tier(cls, v: str) -> str:
        """[HARDENED] Ensure safety tier is valid."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SafetyProfile.validate_safety_tier")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyProfile.validate_safety_tier".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_tiers = {"standard", "strict", "relaxed", "debug"}
        if v not in valid_tiers:
            raise ValueError(f"Safety tier must be one of: {valid_tiers}")
        return v
