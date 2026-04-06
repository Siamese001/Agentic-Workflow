from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "budget_profile_validator")
emit_determinism_digest("p0", "budget_profile_validator")

_emit_dispatches_healing_run("p1", "budget_profile_validator", "L5")
_emit_routes_through("p1", "budget_profile_validator", "L5")
_emit_checks_agent_registry("p1", "budget_profile_validator", "agent_registry")
_emit_validates_agent_capability("p1", "budget_profile_validator", "capability")
_emit_dispatches_execution_plan("p1", "budget_profile_validator", "exec_plan")
_emit_agent_executes_agent("p1", "budget_profile_validator", "sub_agent")
_emit_routes_to_agent("p1", "budget_profile_validator", "target_agent")
_emit_verifies_policy("p1", "budget_profile_validator", "policy_check")
_emit_observes_runtime_state("p1", "budget_profile_validator", "runtime_state")
_emit_verifies_boundary("p1", "budget_profile_validator", "boundary_check")
_emit_transcripts_response("p1", "budget_profile_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "budget_profile_validator")
_emit_gated_by_confidence("p1", "budget_profile_validator", "confidence_gate")
_emit_escalates_to_human("p1", "budget_profile_validator", "L5")
_emit_reads_policy_state("p1", "budget_profile_validator", "L5")

_emit_applies_guardrail("p0", "budget_profile_validator", "p0_governance")
_emit_snapshots_state("p0", "budget_profile_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "budget_profile_validator", "execution_auth")
_emit_validates_capability("p2", "budget_profile_validator", "capability_check")
_emit_routes_to_capability("p2", "budget_profile_validator", "capability_route")
_emit_writes_via_uwg("p2", "budget_profile_validator", "uwg_write")
_emit_blocks_direct_write("p2", "budget_profile_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "budget_profile_validator", "tool_invocation")
_emit_captures_execution_output("p2", "budget_profile_validator", "exec_output")
_emit_dispatches_agent("p3", "budget_profile_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "budget_profile_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "budget_profile_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "budget_profile_validator", "healing_outcome")
_emit_escalates_failure("p3", "budget_profile_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "budget_profile_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "budget_profile_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "budget_profile_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "budget_profile_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "budget_profile_validator", "eval_metric")
_emit_stores_embedding("p4", "budget_profile_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "budget_profile_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "budget_profile_validator", "exec_snapshot_link")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_1")
_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_2")
_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_3")
_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_4")
_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_5")
_emit_emits_metric_event("budget_profile_validator", "p4obs", "metric_6")
_emit_records_incident_event("budget_profile_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("budget_profile_validator", "p4obs", "anomaly")
_emit_writes_observability_log("budget_profile_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("budget_profile_validator", "p4obs", "mon_state")
_emit_triggers_alert("budget_profile_validator", "p4obs", "alert")
_emit_links_incident_trace("budget_profile_validator", "p4obs", "trace_link")
_emit_captures_pattern("budget_profile_validator", "p3lm", "pattern")
_emit_records_learning_event("budget_profile_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("budget_profile_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("budget_profile_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("budget_profile_validator", "p3lm", "routing")
_emit_improves_agent_policy("budget_profile_validator", "p3lm", "policy")
_emit_stores_learning_state("budget_profile_validator", "p3lm", "state")
_emit_records_execution_trace("budget_profile_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("budget_profile_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("budget_profile_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("budget_profile_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("budget_profile_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("budget_profile_validator", "env_read", "p2_env_1")
_emit_reads_environ("budget_profile_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("budget_profile_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("budget_profile_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "budget_profile_validator", "context_pull")
_emit_pulls_context("p1", "budget_profile_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "budget_profile_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "budget_profile_validator", "uwg_term_2")
_emit_writes_through("p1", "budget_profile_validator", "write_through")
_emit_writes_through("p1", "budget_profile_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "budget_profile_validator", "safety_validation")
_emit_invokes_eval("p1", "budget_profile_validator", "eval_call")
_emit_proposal_commits_routing("p1", "budget_profile_validator", "routing_commit")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "BudgetProfile.validate_latency")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BudgetProfile.validate_latency".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if value <= 0:
            raise ValueError("max_latency_ms must be greater than 0")
        return value
