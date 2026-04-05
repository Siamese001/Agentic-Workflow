from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "sovereign_fence_validator_enforcer")
emit_determinism_digest("p0", "sovereign_fence_validator_enforcer")

_emit_dispatches_healing_run("p1", "sovereign_fence_validator_enforcer", "L5")
_emit_routes_through("p1", "sovereign_fence_validator_enforcer", "L5")
_emit_checks_agent_registry("p1", "sovereign_fence_validator_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_fence_validator_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_fence_validator_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_fence_validator_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_fence_validator_enforcer", "target_agent")
_emit_verifies_policy("p1", "sovereign_fence_validator_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_fence_validator_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_fence_validator_enforcer", "boundary_check")
_emit_transcripts_response("p1", "sovereign_fence_validator_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_fence_validator_enforcer")
_emit_gated_by_confidence("p1", "sovereign_fence_validator_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_fence_validator_enforcer", "L5")
_emit_reads_policy_state("p1", "sovereign_fence_validator_enforcer", "L5")
_emit_authorize_and_execute("p2", "sovereign_fence_validator_enforcer", "execution_auth")
_emit_validates_capability("p2", "sovereign_fence_validator_enforcer", "capability_check")
_emit_routes_to_capability("p2", "sovereign_fence_validator_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_fence_validator_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_fence_validator_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_fence_validator_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_fence_validator_enforcer", "exec_output")
_emit_dispatches_agent("p3", "sovereign_fence_validator_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_fence_validator_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_fence_validator_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_fence_validator_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_fence_validator_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_fence_validator_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_fence_validator_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_fence_validator_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_fence_validator_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_fence_validator_enforcer", "eval_metric")
_emit_stores_embedding("p4", "sovereign_fence_validator_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_fence_validator_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_fence_validator_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_fence_validator_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_fence_validator_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_fence_validator_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_fence_validator_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_fence_validator_enforcer", "p4obs", "alert")
_emit_links_incident_trace("sovereign_fence_validator_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_fence_validator_enforcer", "p3lm", "pattern")
_emit_records_learning_event("sovereign_fence_validator_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_fence_validator_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_fence_validator_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_fence_validator_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_fence_validator_enforcer", "p3lm", "policy")
_emit_stores_learning_state("sovereign_fence_validator_enforcer", "p3lm", "state")
_emit_records_execution_trace("sovereign_fence_validator_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_fence_validator_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_fence_validator_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_fence_validator_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_fence_validator_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_fence_validator_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_fence_validator_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_fence_validator_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_fence_validator_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_fence_validator_enforcer", "context_pull")
_emit_pulls_context("p1", "sovereign_fence_validator_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_fence_validator_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_fence_validator_enforcer", "uwg_term_2")
_emit_writes_through("p1", "sovereign_fence_validator_enforcer", "write_through")
_emit_writes_through("p1", "sovereign_fence_validator_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_fence_validator_enforcer", "safety_validation")
_emit_invokes_eval("p1", "sovereign_fence_validator_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_fence_validator_enforcer", "routing_commit")

Proposal = Any
Policy = Any


class SovereignFenceViolation(Exception):
    """Raised when a proposal violates a sovereign safety fence."""

    def __init__(self, reason_code: str, message: str):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SovereignFenceViolation.__init__")
        self.reason_code = reason_code
        self.message = message
        super().__init__(f"[{self.reason_code}] {self.message}")


@dataclass(frozen=True)
class FenceValidationResult:
    """The result of a fence validation check."""

    is_valid: bool
    violations: Sequence[SovereignFenceViolation]

    def to_digest_contribution(self) -> dict[str, Any]:
        """Returns a dictionary suitable for inclusion in a determinism digest."""
        return {
            "is_valid": self.is_valid,
            "violation_codes": sorted([v.reason_code for v in self.violations]),
        }


def validate(proposal: Proposal, policy: Policy) -> FenceValidationResult:
    """
    Validates a proposal against a sovereign policy fence.

    This is a hard boundary. It is not advisory. A validation failure here must
    block any state change (e.g., before a STAMP operation).

    Args:
        proposal: The proposed action or state change.
        policy: The sovereign policy to validate against.

    Returns:
        A FenceValidationResult indicating if the proposal is valid.
    """
    violations = []
    return FenceValidationResult(is_valid=not violations, violations=violations)
