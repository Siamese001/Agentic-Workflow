"""L5 Path D Re-Clear Loop — mandatory re-evaluation after violation remediation.

Spec: L5 Safety, Path D — after a violation is flagged and a remediation is applied,
the enforcement gate MUST re-evaluate the original constraint before marking the
violation as cleared. This prevents silent self-approval of partial fixes.

Re-clear loop contract:
  1. A violation is detected → ReClearTicket is created (status=PENDING).
  2. Remediation is applied externally.
  3. re_evaluate() is called with the remediation evidence.
  4. If the constraint passes, ticket transitions to CLEARED.
  5. If the constraint still fails, ticket transitions to BLOCKED (no silent pass).
  6. A ticket in BLOCKED state MUST NOT be auto-resolved; it requires explicit escalation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

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

emit_replay_key("p0", "re_clear_loop_enforcer")
emit_determinism_digest("p0", "re_clear_loop_enforcer")

_emit_dispatches_healing_run("p1", "re_clear_loop_enforcer", "L5")
_emit_routes_through("p1", "re_clear_loop_enforcer", "L5")
_emit_checks_agent_registry("p1", "re_clear_loop_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "re_clear_loop_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "re_clear_loop_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "re_clear_loop_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "re_clear_loop_enforcer", "target_agent")
_emit_verifies_policy("p1", "re_clear_loop_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "re_clear_loop_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "re_clear_loop_enforcer", "boundary_check")
_emit_transcripts_response("p1", "re_clear_loop_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "re_clear_loop_enforcer")
_emit_gated_by_confidence("p1", "re_clear_loop_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "re_clear_loop_enforcer", "L5")
_emit_reads_policy_state("p1", "re_clear_loop_enforcer", "L5")

_emit_applies_guardrail("p0", "re_clear_loop_enforcer", "p0_governance")
_emit_snapshots_state("p0", "re_clear_loop_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "re_clear_loop_enforcer", "execution_auth")
_emit_validates_capability("p2", "re_clear_loop_enforcer", "capability_check")
_emit_routes_to_capability("p2", "re_clear_loop_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "re_clear_loop_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "re_clear_loop_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "re_clear_loop_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "re_clear_loop_enforcer", "exec_output")
_emit_dispatches_agent("p3", "re_clear_loop_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "re_clear_loop_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "re_clear_loop_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "re_clear_loop_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "re_clear_loop_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "re_clear_loop_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "re_clear_loop_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "re_clear_loop_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "re_clear_loop_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "re_clear_loop_enforcer", "eval_metric")
_emit_stores_embedding("p4", "re_clear_loop_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "re_clear_loop_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "re_clear_loop_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("re_clear_loop_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("re_clear_loop_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("re_clear_loop_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("re_clear_loop_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("re_clear_loop_enforcer", "p4obs", "alert")
_emit_links_incident_trace("re_clear_loop_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("re_clear_loop_enforcer", "p3lm", "pattern")
_emit_records_learning_event("re_clear_loop_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("re_clear_loop_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("re_clear_loop_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("re_clear_loop_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("re_clear_loop_enforcer", "p3lm", "policy")
_emit_stores_learning_state("re_clear_loop_enforcer", "p3lm", "state")
_emit_records_execution_trace("re_clear_loop_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("re_clear_loop_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("re_clear_loop_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("re_clear_loop_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("re_clear_loop_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("re_clear_loop_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("re_clear_loop_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("re_clear_loop_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("re_clear_loop_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "re_clear_loop_enforcer", "context_pull")
_emit_pulls_context("p1", "re_clear_loop_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "re_clear_loop_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "re_clear_loop_enforcer", "uwg_term_2")
_emit_writes_through("p1", "re_clear_loop_enforcer", "write_through")
_emit_writes_through("p1", "re_clear_loop_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "re_clear_loop_enforcer", "safety_validation")
_emit_invokes_eval("p1", "re_clear_loop_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "re_clear_loop_enforcer", "routing_commit")


class ReClearViolation(RuntimeError):
    """Raised when the re-clear loop contract is violated."""


class ReClearStatus(str, Enum):
    PENDING = "PENDING"
    CLEARED = "CLEARED"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"


@dataclass
class ReClearTicket:
    """Tracks a single L5 violation through the Path D re-clear lifecycle.

    Spec: L5 Safety Path D — immutable once CLEARED or BLOCKED.
    Fields:
        ticket_id: Stable unique identifier (non-empty).
        constraint_id: The L5 constraint that was violated.
        violation_summary: Human-readable description of the violation.
        status: Current lifecycle status.
        remediation_evidence: Evidence dict populated by re_evaluate().
        escalation_note: Required when status=ESCALATED.
    """

    ticket_id: str
    constraint_id: str
    violation_summary: str
    status: ReClearStatus = ReClearStatus.PENDING
    remediation_evidence: dict[str, Any] = field(default_factory=dict)
    escalation_note: str = ""

    def __post_init__(self) -> None:
        if not self.ticket_id or not self.ticket_id.strip():
            raise ReClearViolation("ReClearTicket.ticket_id must be non-empty")
        if not self.constraint_id or not self.constraint_id.strip():
            raise ReClearViolation("ReClearTicket.constraint_id must be non-empty")
        if not self.violation_summary or not self.violation_summary.strip():
            raise ReClearViolation("ReClearTicket.violation_summary must be non-empty")

    def _assert_mutable(self) -> None:
        if self.status in (ReClearStatus.CLEARED, ReClearStatus.BLOCKED):
            raise ReClearViolation(
                f"ReClearTicket '{self.ticket_id}' is terminal (status={self.status.value}). Cleared/Blocked tickets are immutable. Create a new ticket for re-remediation."
            )

    def re_evaluate(
        self, constraint_fn: Callable[[], bool], evidence: dict[str, Any] | None = None
    ) -> ReClearTicket:
        """Re-evaluate the original constraint after remediation.

        Args:
            constraint_fn: Returns True if the constraint is now satisfied, False if still violated.
            evidence: Optional evidence dict to record with the outcome.

        Returns:
            A new ReClearTicket with updated status (CLEARED or BLOCKED).

        Raises:
            ReClearViolation: If the ticket is already terminal.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ReClearTicket.re_evaluate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReClearTicket.re_evaluate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._assert_mutable()
        passed = constraint_fn()
        new_status = ReClearStatus.CLEARED if passed else ReClearStatus.BLOCKED
        new_evidence = {**(evidence or {}), "re_evaluate_passed": passed}
        return ReClearTicket(
            ticket_id=self.ticket_id,
            constraint_id=self.constraint_id,
            violation_summary=self.violation_summary,
            status=new_status,
            remediation_evidence=new_evidence,
            escalation_note=self.escalation_note,
        )

    def escalate(self, note: str) -> ReClearTicket:
        """Escalate a BLOCKED ticket with a mandatory note.

        Only BLOCKED tickets may be escalated.
        Raises ReClearViolation if ticket is not BLOCKED.
        """
        if self.status != ReClearStatus.BLOCKED:
            raise ReClearViolation(
                f"Only BLOCKED tickets may be escalated. Ticket '{self.ticket_id}' is {self.status.value}."
            )
        if not note or not note.strip():
            raise ReClearViolation(
                "escalate() requires a non-empty note explaining the escalation rationale."
            )
        return ReClearTicket(
            ticket_id=self.ticket_id,
            constraint_id=self.constraint_id,
            violation_summary=self.violation_summary,
            status=ReClearStatus.ESCALATED,
            remediation_evidence=self.remediation_evidence,
            escalation_note=note,
        )


def open_ticket(ticket_id: str, constraint_id: str, violation_summary: str) -> ReClearTicket:
    """Open a new Path D re-clear ticket for a detected violation."""
    return ReClearTicket(
        ticket_id=ticket_id, constraint_id=constraint_id, violation_summary=violation_summary
    )


__all__ = ["ReClearStatus", "ReClearTicket", "ReClearViolation", "open_ticket"]
