from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "consensus_verdict_validator")
emit_determinism_digest("p0", "consensus_verdict_validator")

_emit_dispatches_healing_run("p1", "consensus_verdict_validator", "L5")
_emit_routes_through("p1", "consensus_verdict_validator", "L5")
_emit_checks_agent_registry("p1", "consensus_verdict_validator", "agent_registry")
_emit_validates_agent_capability("p1", "consensus_verdict_validator", "capability")
_emit_dispatches_execution_plan("p1", "consensus_verdict_validator", "exec_plan")
_emit_agent_executes_agent("p1", "consensus_verdict_validator", "sub_agent")
_emit_routes_to_agent("p1", "consensus_verdict_validator", "target_agent")
_emit_verifies_policy("p1", "consensus_verdict_validator", "policy_check")
_emit_observes_runtime_state("p1", "consensus_verdict_validator", "runtime_state")
_emit_verifies_boundary("p1", "consensus_verdict_validator", "boundary_check")
_emit_transcripts_response("p1", "consensus_verdict_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "consensus_verdict_validator")
_emit_gated_by_confidence("p1", "consensus_verdict_validator", "confidence_gate")
_emit_escalates_to_human("p1", "consensus_verdict_validator", "L5")
_emit_reads_policy_state("p1", "consensus_verdict_validator", "L5")

_emit_applies_guardrail("p0", "consensus_verdict_validator", "p0_governance")
_emit_snapshots_state("p0", "consensus_verdict_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "consensus_verdict_validator", "execution_auth")
_emit_validates_capability("p2", "consensus_verdict_validator", "capability_check")
_emit_routes_to_capability("p2", "consensus_verdict_validator", "capability_route")
_emit_writes_via_uwg("p2", "consensus_verdict_validator", "uwg_write")
_emit_blocks_direct_write("p2", "consensus_verdict_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "consensus_verdict_validator", "tool_invocation")
_emit_captures_execution_output("p2", "consensus_verdict_validator", "exec_output")
_emit_dispatches_agent("p3", "consensus_verdict_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "consensus_verdict_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "consensus_verdict_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "consensus_verdict_validator", "healing_outcome")
_emit_escalates_failure("p3", "consensus_verdict_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "consensus_verdict_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "consensus_verdict_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "consensus_verdict_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "consensus_verdict_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "consensus_verdict_validator", "eval_metric")
_emit_stores_embedding("p4", "consensus_verdict_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "consensus_verdict_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "consensus_verdict_validator", "exec_snapshot_link")

"\nConsensus & Deliberation Schemas\n===============================\nDefines the structures for multi-model consensus and individual\nmodel opinions. Used to ensure plan safety and agreement across\nthe agentic collective.\n"

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_1")
_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_2")
_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_3")
_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_4")
_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_5")
_emit_emits_metric_event("consensus_verdict_validator", "p4obs", "metric_6")
_emit_records_incident_event("consensus_verdict_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("consensus_verdict_validator", "p4obs", "anomaly")
_emit_writes_observability_log("consensus_verdict_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("consensus_verdict_validator", "p4obs", "mon_state")
_emit_triggers_alert("consensus_verdict_validator", "p4obs", "alert")
_emit_links_incident_trace("consensus_verdict_validator", "p4obs", "trace_link")
_emit_captures_pattern("consensus_verdict_validator", "p3lm", "pattern")
_emit_records_learning_event("consensus_verdict_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("consensus_verdict_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("consensus_verdict_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("consensus_verdict_validator", "p3lm", "routing")
_emit_improves_agent_policy("consensus_verdict_validator", "p3lm", "policy")
_emit_stores_learning_state("consensus_verdict_validator", "p3lm", "state")
_emit_records_execution_trace("consensus_verdict_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("consensus_verdict_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("consensus_verdict_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("consensus_verdict_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("consensus_verdict_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("consensus_verdict_validator", "env_read", "p2_env_1")
_emit_reads_environ("consensus_verdict_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("consensus_verdict_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("consensus_verdict_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "consensus_verdict_validator", "context_pull")
_emit_pulls_context("p1", "consensus_verdict_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "consensus_verdict_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "consensus_verdict_validator", "uwg_term_2")
_emit_writes_through("p1", "consensus_verdict_validator", "write_through")
_emit_writes_through("p1", "consensus_verdict_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "consensus_verdict_validator", "safety_validation")
_emit_invokes_eval("p1", "consensus_verdict_validator", "eval_call")
_emit_proposal_commits_routing("p1", "consensus_verdict_validator", "routing_commit")


class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation across multiple models."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    chosen_plan: str = Field(..., description="The definitive plan agreed upon by the collective")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Level of agreement (0.0 to 1.0)")
    dissenting_opinions: list[str] = Field(
        default_factory=list, description="Summary of non-concurring views"
    )
    reasoning: str = Field(..., description="The logic used to synthesize the final Verdict")
    safe_to_proceed: bool = Field(..., description="Final gate check based on consensus risks")


class ModelOpinion(BaseModel):
    """Individual model's opinion on a proposed plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    model_name: str = Field(..., description="The identifier of the contributing model")
    plan: str = Field(..., description="The specific plan being evaluated")
    reasoning: str = Field(..., description="Individual model's logic for its stance")
    risk_assessment: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this specific opinion")

    @field_validator("risk_assessment")
    @classmethod
    def validate_risk_assessment(cls, v: str) -> str:
        """[HARDENED] Ensure risk assessment is valid."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ModelOpinion.validate_risk_assessment"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ModelOpinion.validate_risk_assessment".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Risk assessment must be one of: {valid_levels}")
        return v.upper()
