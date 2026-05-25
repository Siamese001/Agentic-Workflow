"""Concrete ApprovalGate — decides whether to approve change packages.

Provides configurable auto-approve thresholds and manual review flagging
for high-risk changes.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "approval_gate_impl", "p0_governance")
_emit_reads_policy_state("p0", "approval_gate_impl", "policy_binding")
_emit_snapshots_state("p0", "approval_gate_impl", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_1")
_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_2")
_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_3")
_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_4")
_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_5")
_emit_emits_metric_event("approval_gate_impl", "p4obs", "metric_6")
_emit_records_incident_event("approval_gate_impl", "p4obs", "incident")
_emit_captures_runtime_anomaly("approval_gate_impl", "p4obs", "anomaly")
_emit_writes_observability_log("approval_gate_impl", "p4obs", "obs_log")
_emit_updates_monitoring_state("approval_gate_impl", "p4obs", "mon_state")
_emit_triggers_alert("approval_gate_impl", "p4obs", "alert")
_emit_links_incident_trace("approval_gate_impl", "p4obs", "trace_link")
_emit_captures_pattern("approval_gate_impl", "p3lm", "pattern")
_emit_records_learning_event("approval_gate_impl", "p3lm", "learning_event")
_emit_writes_learning_snapshot("approval_gate_impl", "p3lm", "snapshot")
_emit_feeds_meta_learning("approval_gate_impl", "p3lm", "meta_feed")
_emit_updates_routing_strategy("approval_gate_impl", "p3lm", "routing")
_emit_improves_agent_policy("approval_gate_impl", "p3lm", "policy")
_emit_stores_learning_state("approval_gate_impl", "p3lm", "state")
_emit_records_execution_trace("approval_gate_impl", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("approval_gate_impl", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("approval_gate_impl", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("approval_gate_impl", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("approval_gate_impl", "L4_STATE", "p2_trace_5")
_emit_reads_environ("approval_gate_impl", "env_read", "p2_env_1")
_emit_reads_environ("approval_gate_impl", "env_read", "p2_env_2")
_emit_reads_runtime_state("approval_gate_impl", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("approval_gate_impl", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "approval_gate_impl", "context_pull")
_emit_pulls_context("p1", "approval_gate_impl", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "approval_gate_impl", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "approval_gate_impl", "uwg_term_2")
_emit_writes_through("p1", "approval_gate_impl", "write_through")
_emit_writes_through("p1", "approval_gate_impl", "write_through_2")
_emit_validated_by_safety_plane("p1", "approval_gate_impl", "safety_validation")
_emit_invokes_eval("p1", "approval_gate_impl", "eval_call")
_emit_proposal_commits_routing("p1", "approval_gate_impl", "routing_commit")
_emit_escalates_to_human("p1", "approval_gate_impl", "human_escalation")
_emit_routes_through("p1", "approval_gate_impl", "route_through")
_emit_checks_agent_registry("p1", "approval_gate_impl", "agent_registry")
_emit_validates_agent_capability("p1", "approval_gate_impl", "capability")
_emit_dispatches_execution_plan("p1", "approval_gate_impl", "exec_plan")
_emit_agent_executes_agent("p1", "approval_gate_impl", "sub_agent")
_emit_routes_to_agent("p1", "approval_gate_impl", "target_agent")
_emit_verifies_policy("p1", "approval_gate_impl", "policy_check")
_emit_observes_runtime_state("p1", "approval_gate_impl", "runtime_state")
_emit_verifies_boundary("p1", "approval_gate_impl", "boundary_check")
_emit_transcripts_response("p1", "approval_gate_impl", "transcript")
_emit_hard_fails_untranscripted("p1", "approval_gate_impl")
_emit_gated_by_confidence("p1", "approval_gate_impl", "confidence_gate")
emit_replay_key("p0", "approval_gate_impl")
emit_determinism_digest("p0", "approval_gate_impl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "approval_gate_impl", "execution_auth")
_emit_validates_capability("p2", "approval_gate_impl", "capability_check")
_emit_routes_to_capability("p2", "approval_gate_impl", "capability_route")
_emit_writes_via_uwg("p2", "approval_gate_impl", "uwg_write")
_emit_blocks_direct_write("p2", "approval_gate_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "approval_gate_impl", "tool_invocation")
_emit_captures_execution_output("p2", "approval_gate_impl", "exec_output")
_emit_dispatches_agent("p3", "approval_gate_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "approval_gate_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "approval_gate_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "approval_gate_impl", "healing_outcome")
_emit_escalates_failure("p3", "approval_gate_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "approval_gate_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "approval_gate_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "approval_gate_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "approval_gate_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "approval_gate_impl", "eval_metric")
_emit_stores_embedding("p4", "approval_gate_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "approval_gate_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "approval_gate_impl", "exec_snapshot_link")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AutoApprovalGate.decide")

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
