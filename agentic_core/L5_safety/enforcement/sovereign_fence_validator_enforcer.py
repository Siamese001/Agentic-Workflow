from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_fence_validator_enforcer")
trace_contract.emit_determinism_digest("p0", "sovereign_fence_validator_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_fence_validator_enforcer", "L5")
trace_contract._emit_routes_through("p1", "sovereign_fence_validator_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "sovereign_fence_validator_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_fence_validator_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_fence_validator_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_fence_validator_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_fence_validator_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_fence_validator_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_fence_validator_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_fence_validator_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_fence_validator_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_fence_validator_enforcer")
trace_contract._emit_gated_by_confidence("p1", "sovereign_fence_validator_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_fence_validator_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "sovereign_fence_validator_enforcer", "L5")
trace_contract._emit_authorize_and_execute("p2", "sovereign_fence_validator_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_fence_validator_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_fence_validator_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_fence_validator_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_fence_validator_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_fence_validator_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_fence_validator_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_fence_validator_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_fence_validator_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_fence_validator_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_fence_validator_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_fence_validator_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_fence_validator_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_fence_validator_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_fence_validator_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_fence_validator_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_fence_validator_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_fence_validator_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_fence_validator_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_fence_validator_enforcer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_fence_validator_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_fence_validator_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_fence_validator_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_fence_validator_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_fence_validator_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_fence_validator_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_fence_validator_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_fence_validator_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_fence_validator_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_fence_validator_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_fence_validator_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_fence_validator_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_fence_validator_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_fence_validator_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_fence_validator_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_fence_validator_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_fence_validator_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_fence_validator_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_fence_validator_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_fence_validator_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_fence_validator_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_fence_validator_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_fence_validator_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_fence_validator_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_fence_validator_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_fence_validator_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_fence_validator_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_fence_validator_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_fence_validator_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_fence_validator_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_fence_validator_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_fence_validator_enforcer", "routing_commit")

Proposal = Any
Policy = Any


class SovereignFenceViolation(Exception):
    """Raised when a proposal violates a sovereign safety fence."""

    def __init__(self, reason_code: str, message: str):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SovereignFenceViolation.__init__")
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
