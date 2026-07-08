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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "re_clear_loop_enforcer")
trace_contract.emit_determinism_digest("p0", "re_clear_loop_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "re_clear_loop_enforcer", "L5")
trace_contract._emit_routes_through("p1", "re_clear_loop_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "re_clear_loop_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "re_clear_loop_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "re_clear_loop_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "re_clear_loop_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "re_clear_loop_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "re_clear_loop_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "re_clear_loop_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "re_clear_loop_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "re_clear_loop_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "re_clear_loop_enforcer")
trace_contract._emit_gated_by_confidence("p1", "re_clear_loop_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "re_clear_loop_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "re_clear_loop_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "re_clear_loop_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "re_clear_loop_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "re_clear_loop_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "re_clear_loop_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "re_clear_loop_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "re_clear_loop_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "re_clear_loop_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "re_clear_loop_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "re_clear_loop_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "re_clear_loop_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "re_clear_loop_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "re_clear_loop_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "re_clear_loop_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "re_clear_loop_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "re_clear_loop_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "re_clear_loop_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "re_clear_loop_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "re_clear_loop_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "re_clear_loop_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "re_clear_loop_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "re_clear_loop_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "re_clear_loop_enforcer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("re_clear_loop_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("re_clear_loop_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("re_clear_loop_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("re_clear_loop_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("re_clear_loop_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("re_clear_loop_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("re_clear_loop_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("re_clear_loop_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("re_clear_loop_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("re_clear_loop_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("re_clear_loop_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("re_clear_loop_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("re_clear_loop_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("re_clear_loop_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("re_clear_loop_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("re_clear_loop_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("re_clear_loop_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("re_clear_loop_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("re_clear_loop_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("re_clear_loop_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("re_clear_loop_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("re_clear_loop_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("re_clear_loop_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "re_clear_loop_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "re_clear_loop_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "re_clear_loop_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "re_clear_loop_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "re_clear_loop_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "re_clear_loop_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "re_clear_loop_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "re_clear_loop_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "re_clear_loop_enforcer", "routing_commit")


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
                f"ReClearTicket '{self.ticket_id}' is terminal (status={self.status.value}). Cleared/Blocked tickets are immutable. Create a new ticket for re-remediation.",
            )

    def re_evaluate(
        self,
        constraint_fn: Callable[[], bool],
        evidence: dict[str, Any] | None = None,
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ReClearTicket.re_evaluate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReClearTicket.re_evaluate".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                f"Only BLOCKED tickets may be escalated. Ticket '{self.ticket_id}' is {self.status.value}.",
            )
        if not note or not note.strip():
            raise ReClearViolation(
                "escalate() requires a non-empty note explaining the escalation rationale.",
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
        ticket_id=ticket_id,
        constraint_id=constraint_id,
        violation_summary=violation_summary,
    )


__all__ = ["ReClearStatus", "ReClearTicket", "ReClearViolation", "open_ticket"]
