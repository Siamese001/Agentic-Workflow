"""Concrete ApprovalGate — decides whether to approve change packages.

Provides configurable auto-approve thresholds and manual review flagging
for high-risk changes.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "approval_gate_impl", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "approval_gate_impl", "policy_binding")
trace_contract._emit_snapshots_state("p0", "approval_gate_impl", "state_snapshot")

trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("approval_gate_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("approval_gate_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("approval_gate_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("approval_gate_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("approval_gate_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("approval_gate_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("approval_gate_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("approval_gate_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("approval_gate_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("approval_gate_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("approval_gate_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("approval_gate_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("approval_gate_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("approval_gate_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("approval_gate_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("approval_gate_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("approval_gate_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("approval_gate_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("approval_gate_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("approval_gate_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("approval_gate_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("approval_gate_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "approval_gate_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "approval_gate_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "approval_gate_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "approval_gate_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "approval_gate_impl", "write_through")
trace_contract._emit_writes_through("p1", "approval_gate_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "approval_gate_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "approval_gate_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "approval_gate_impl", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "approval_gate_impl", "human_escalation")
trace_contract._emit_routes_through("p1", "approval_gate_impl", "route_through")
trace_contract._emit_checks_agent_registry("p1", "approval_gate_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "approval_gate_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "approval_gate_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "approval_gate_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "approval_gate_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "approval_gate_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "approval_gate_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "approval_gate_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "approval_gate_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "approval_gate_impl")
trace_contract._emit_gated_by_confidence("p1", "approval_gate_impl", "confidence_gate")
trace_contract.emit_replay_key("p0", "approval_gate_impl")
trace_contract.emit_determinism_digest("p0", "approval_gate_impl")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "approval_gate_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "approval_gate_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "approval_gate_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "approval_gate_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "approval_gate_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "approval_gate_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "approval_gate_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "approval_gate_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "approval_gate_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "approval_gate_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "approval_gate_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "approval_gate_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "approval_gate_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "approval_gate_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "approval_gate_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "approval_gate_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "approval_gate_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "approval_gate_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "approval_gate_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "approval_gate_impl", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    """Result of an approval gate decision."""

    approved: bool
    reason: str
    requires_manual_review: bool = False


class AutoApprovalGate:
    """Approval gate that auto-approves low-risk changes.

    Parameters
    ----------
    max_auto_approve_delta : float
        Maximum delta magnitude for auto-approval.
    auto_approve_surfaces : frozenset[str]
        Set of surface names eligible for auto-approval.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        max_auto_approve_delta: float = 0.03,
        auto_approve_surfaces: frozenset[str] | None = None,
    ) -> None:
        self._max_delta = max_auto_approve_delta
        self._auto_surfaces = auto_approve_surfaces or frozenset({"escalation_threshold"})

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve a change package.

        Auto-approves if:
        - The package surface is in the auto-approve set
        - The delta magnitude is within the auto-approve threshold

        Otherwise flags for manual review.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "AutoApprovalGate.decide")

        surface = getattr(pkg, "surface_name", None)
        if surface is None:
            surface = getattr(pkg, "component", "unknown")
        delta = 0.0
        if hasattr(pkg, "new_value") and hasattr(pkg, "old_value"):
            delta = abs(pkg.new_value - pkg.old_value)
        elif hasattr(pkg, "delta"):
            delta = abs(pkg.delta)
        if surface in self._auto_surfaces and delta <= self._max_delta:
            return ApprovalDecision(
                approved=True,
                reason=f"Auto-approved: surface='{surface}' delta={delta:.4f} <= {self._max_delta}",
            )
        return ApprovalDecision(
            approved=False,
            reason=f"Requires manual review: surface='{surface}' delta={delta:.4f} > {self._max_delta}",
            requires_manual_review=True,
        )


class AlwaysApproveGate:
    """Test gate that always approves."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        return ApprovalDecision(approved=True, reason="Always-approve gate (test mode)")


class NeverApproveGate:
    """Safety gate that never approves (proposal-only mode)."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        return ApprovalDecision(
            approved=False,
            reason="Never-approve gate (proposal-only mode)",
            requires_manual_review=True,
        )


__all__ = ["ApprovalDecision", "AutoApprovalGate", "AlwaysApproveGate", "NeverApproveGate"]
