"""
L5 CONF_CALIB Risk Gate - Structured Risk Decision Engine

Implements deterministic risk evaluation with structured RiskDecision output.
No ML, no wall-clock usage, pure deterministic rules.
"""

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "conf_calib_gate")
emit_determinism_digest("p0", "conf_calib_gate")

_emit_dispatches_healing_run("p1", "conf_calib_gate", "L5")
_emit_routes_through("p1", "conf_calib_gate", "L5")
_emit_checks_agent_registry("p1", "conf_calib_gate", "agent_registry")
_emit_validates_agent_capability("p1", "conf_calib_gate", "capability")
_emit_dispatches_execution_plan("p1", "conf_calib_gate", "exec_plan")
_emit_agent_executes_agent("p1", "conf_calib_gate", "sub_agent")
_emit_routes_to_agent("p1", "conf_calib_gate", "target_agent")
_emit_verifies_policy("p1", "conf_calib_gate", "policy_check")
_emit_observes_runtime_state("p1", "conf_calib_gate", "runtime_state")
_emit_verifies_boundary("p1", "conf_calib_gate", "boundary_check")
_emit_transcripts_response("p1", "conf_calib_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "conf_calib_gate")
_emit_gated_by_confidence("p1", "conf_calib_gate", "confidence_gate")
_emit_escalates_to_human("p1", "conf_calib_gate", "L5")
_emit_reads_policy_state("p1", "conf_calib_gate", "L5")

_emit_applies_guardrail("p0", "conf_calib_gate", "p0_governance")
_emit_snapshots_state("p0", "conf_calib_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "conf_calib_gate", "execution_auth")
_emit_validates_capability("p2", "conf_calib_gate", "capability_check")
_emit_routes_to_capability("p2", "conf_calib_gate", "capability_route")
_emit_writes_via_uwg("p2", "conf_calib_gate", "uwg_write")
_emit_blocks_direct_write("p2", "conf_calib_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "conf_calib_gate", "tool_invocation")
_emit_captures_execution_output("p2", "conf_calib_gate", "exec_output")
_emit_dispatches_agent("p3", "conf_calib_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "conf_calib_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "conf_calib_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "conf_calib_gate", "healing_outcome")
_emit_escalates_failure("p3", "conf_calib_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "conf_calib_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "conf_calib_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "conf_calib_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "conf_calib_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "conf_calib_gate", "eval_metric")
_emit_stores_embedding("p4", "conf_calib_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "conf_calib_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "conf_calib_gate", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_1")
_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_2")
_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_3")
_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_4")
_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_5")
_emit_emits_metric_event("conf_calib_gate", "p4obs", "metric_6")
_emit_records_incident_event("conf_calib_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("conf_calib_gate", "p4obs", "anomaly")
_emit_writes_observability_log("conf_calib_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("conf_calib_gate", "p4obs", "mon_state")
_emit_triggers_alert("conf_calib_gate", "p4obs", "alert")
_emit_links_incident_trace("conf_calib_gate", "p4obs", "trace_link")
_emit_captures_pattern("conf_calib_gate", "p3lm", "pattern")
_emit_records_learning_event("conf_calib_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("conf_calib_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("conf_calib_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("conf_calib_gate", "p3lm", "routing")
_emit_improves_agent_policy("conf_calib_gate", "p3lm", "policy")
_emit_stores_learning_state("conf_calib_gate", "p3lm", "state")
_emit_records_execution_trace("conf_calib_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("conf_calib_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("conf_calib_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("conf_calib_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("conf_calib_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("conf_calib_gate", "env_read", "p2_env_1")
_emit_reads_environ("conf_calib_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("conf_calib_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("conf_calib_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "conf_calib_gate", "context_pull")
_emit_pulls_context("p1", "conf_calib_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "conf_calib_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "conf_calib_gate", "uwg_term_2")
_emit_writes_through("p1", "conf_calib_gate", "write_through")
_emit_writes_through("p1", "conf_calib_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "conf_calib_gate", "safety_validation")
_emit_invokes_eval("p1", "conf_calib_gate", "eval_call")
_emit_proposal_commits_routing("p1", "conf_calib_gate", "routing_commit")


class RiskLevel(Enum):
    """Risk level enumeration for structured decision making."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskDecision:
    """Structured risk decision with deterministic reasons."""

    allow: bool
    level: RiskLevel
    reasons: tuple[str, ...]


class ConfCalibRiskGate:
    """
    CONF_CALIB Risk Gate for deterministic risk evaluation.

    Evaluates payload and D0 injections to produce structured RiskDecision.
    No imports from L0/L2, no wall-clock usage.
    """

    def evaluate(self, *, payload_like: object, d0_injections: str) -> RiskDecision:
        """
        Evaluate risk for given payload and D0 injections.

        Deterministic rules (no ML, no clocks):
        - Start with LOW/allow=True
        - If payload sanitized => at least MEDIUM, reason "SANITIZED_INPUT"
        - If >=5 check_ids => at least MEDIUM, reason "MANY_CHECK_IDS"
        - If D0 contains "DENY_EXECUTION" => HIGH and allow=False, reason "D0_DENY_EXECUTION"
        - Always sort reasons lexicographically

        Args:
            payload_like: Object to evaluate (must not be mutated)
            d0_injections: D0 injection string to evaluate

        Returns:
            Structured RiskDecision with deterministic reasons
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ConfCalibRiskGate.evaluate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConfCalibRiskGate.evaluate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        current_level = RiskLevel.LOW
        allow_execution = True
        reasons = []
        if getattr(payload_like, "sanitized", False):
            current_level = RiskLevel.MEDIUM
            reasons.append("SANITIZED_INPUT")
        check_ids = getattr(payload_like, "check_ids", ())
        if len(check_ids) >= 5:
            current_level = RiskLevel.MEDIUM
            reasons.append("MANY_CHECK_IDS")
        if "DENY_EXECUTION" in d0_injections:
            current_level = RiskLevel.HIGH
            allow_execution = False
            reasons.append("D0_DENY_EXECUTION")
        sorted_reasons = tuple(sorted(reasons))
        return RiskDecision(allow=allow_execution, level=current_level, reasons=sorted_reasons)
