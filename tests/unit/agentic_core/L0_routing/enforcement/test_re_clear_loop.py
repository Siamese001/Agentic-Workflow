"""Tests for L5 Path D Re-Clear Loop contract.

Phase 9: Path D L5 re-clear loop closure.
Spec: L5 Safety Path D — re-evaluation after violation remediation.
"""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_re_clear_loop")
# REMOVED: _emit_applies_guardrail("p0", "test_re_clear_loop", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_re_clear_loop", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_re_clear_loop", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_re_clear_loop")
# REMOVED: emit_determinism_digest("p0", "test_re_clear_loop")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_re_clear_loop", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_re_clear_loop", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_re_clear_loop", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_re_clear_loop", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_re_clear_loop", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_re_clear_loop", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_re_clear_loop", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_re_clear_loop", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_re_clear_loop", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_re_clear_loop", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_re_clear_loop", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_re_clear_loop", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_re_clear_loop", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_re_clear_loop", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_re_clear_loop", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_re_clear_loop", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_re_clear_loop", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_re_clear_loop", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_re_clear_loop", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_re_clear_loop", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.re_clear_loop_enforcer import (
    ReClearStatus,
    ReClearTicket,
    ReClearViolation,
    open_ticket,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_re_clear_loop", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_re_clear_loop", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_re_clear_loop", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_re_clear_loop", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_re_clear_loop", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_re_clear_loop", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_re_clear_loop", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_re_clear_loop", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_re_clear_loop", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_re_clear_loop", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_re_clear_loop", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_re_clear_loop", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_re_clear_loop", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_re_clear_loop", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_re_clear_loop", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_re_clear_loop", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_re_clear_loop", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_re_clear_loop", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_re_clear_loop", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_re_clear_loop", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_re_clear_loop", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_re_clear_loop", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_re_clear_loop", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_re_clear_loop", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_re_clear_loop", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_re_clear_loop", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_re_clear_loop", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_re_clear_loop", "write_through")
# REMOVED: _emit_writes_through("p1", "test_re_clear_loop", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_re_clear_loop", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_re_clear_loop", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_re_clear_loop", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_re_clear_loop", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_re_clear_loop", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_re_clear_loop", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_re_clear_loop", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_re_clear_loop", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_re_clear_loop", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_re_clear_loop", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_re_clear_loop", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_re_clear_loop", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_re_clear_loop", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_re_clear_loop", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_re_clear_loop")
# REMOVED: _emit_gated_by_confidence("p1", "test_re_clear_loop", "confidence_gate")

# ---------------------------------------------------------------------------
# ReClearTicket construction
# ---------------------------------------------------------------------------


class TestReClearTicketConstruction:
    def test_valid_ticket(self):
        t = ReClearTicket(
            ticket_id="T-001",
            constraint_id="G-15-1",
            violation_summary="L5 mutation detected in L0 layer",
        )
        assert t.ticket_id == "T-001"
        assert t.status == ReClearStatus.PENDING

    def test_empty_ticket_id_raises(self):
        with pytest.raises(ReClearViolation, match="ticket_id must be non-empty"):
            ReClearTicket(ticket_id="", constraint_id="G-15-1", violation_summary="v")

    def test_empty_constraint_id_raises(self):
        with pytest.raises(ReClearViolation, match="constraint_id must be non-empty"):
            ReClearTicket(ticket_id="T-001", constraint_id="", violation_summary="v")

    def test_empty_violation_summary_raises(self):
        with pytest.raises(ReClearViolation, match="violation_summary must be non-empty"):
            ReClearTicket(ticket_id="T-001", constraint_id="G-15-1", violation_summary="")

    def test_open_ticket_factory(self):
        t = open_ticket("T-002", "G-12-1", "Persistent write in L4")
        assert t.ticket_id == "T-002"
        assert t.status == ReClearStatus.PENDING
        assert t.remediation_evidence == {}


# ---------------------------------------------------------------------------
# re_evaluate — CLEARED path
# ---------------------------------------------------------------------------


class TestReClearEvaluateClearedPath:
    def test_re_evaluate_passes_when_constraint_satisfied(self):
        t = open_ticket("T-003", "G-15-1", "Write in L0")
        cleared = t.re_evaluate(constraint_fn=lambda: True)
        assert cleared.status == ReClearStatus.CLEARED

    def test_cleared_ticket_records_evidence(self):
        t = open_ticket("T-004", "G-15-1", "Write in L0")
        evidence = {"patch_applied": "abc123", "scanner_passed": True}
        cleared = t.re_evaluate(constraint_fn=lambda: True, evidence=evidence)
        assert cleared.remediation_evidence["patch_applied"] == "abc123"
        assert cleared.remediation_evidence["re_evaluate_passed"] is True

    def test_cleared_ticket_preserves_original_fields(self):
        t = open_ticket("T-005", "G-12-1", "Mutation in L4")
        cleared = t.re_evaluate(constraint_fn=lambda: True)
        assert cleared.ticket_id == "T-005"
        assert cleared.constraint_id == "G-12-1"
        assert cleared.violation_summary == "Mutation in L4"

    def test_re_evaluate_on_cleared_ticket_raises(self):
        t = open_ticket("T-006", "G-15-1", "Write in L0")
        cleared = t.re_evaluate(constraint_fn=lambda: True)
        with pytest.raises(ReClearViolation, match="terminal"):
            cleared.re_evaluate(constraint_fn=lambda: True)


# ---------------------------------------------------------------------------
# re_evaluate — BLOCKED path (constraint still fails)
# ---------------------------------------------------------------------------


class TestReClearEvaluateBlockedPath:
    def test_re_evaluate_blocked_when_constraint_fails(self):
        t = open_ticket("T-007", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        assert blocked.status == ReClearStatus.BLOCKED

    def test_blocked_evidence_records_failure(self):
        t = open_ticket("T-008", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False, evidence={"attempt": 1})
        assert blocked.remediation_evidence["re_evaluate_passed"] is False
        assert blocked.remediation_evidence["attempt"] == 1

    def test_re_evaluate_on_blocked_ticket_raises(self):
        t = open_ticket("T-009", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        with pytest.raises(ReClearViolation, match="terminal"):
            blocked.re_evaluate(constraint_fn=lambda: True)

    def test_blocked_ticket_cannot_be_silently_cleared(self):
        """Negative control: BLOCKED must require explicit escalation, not auto-clear."""
        t = open_ticket("T-010", "G-15-1", "Persistent violation")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        assert blocked.status == ReClearStatus.BLOCKED
        # Verify it cannot self-clear
        with pytest.raises(ReClearViolation, match="terminal"):
            blocked.re_evaluate(constraint_fn=lambda: True)


# ---------------------------------------------------------------------------
# escalate — ESCALATED path
# ---------------------------------------------------------------------------


class TestReClearEscalation:
    def test_escalate_blocked_ticket(self):
        t = open_ticket("T-011", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        escalated = blocked.escalate("Authorized by security-ops: partial remediation accepted")
        assert escalated.status == ReClearStatus.ESCALATED
        assert "security-ops" in escalated.escalation_note

    def test_escalate_pending_ticket_raises(self):
        t = open_ticket("T-012", "G-15-1", "Write in L0")
        with pytest.raises(ReClearViolation, match="Only BLOCKED tickets"):
            t.escalate("note")

    def test_escalate_cleared_ticket_raises(self):
        t = open_ticket("T-013", "G-15-1", "Write in L0")
        cleared = t.re_evaluate(constraint_fn=lambda: True)
        with pytest.raises(ReClearViolation, match="Only BLOCKED tickets"):
            cleared.escalate("note")

    def test_escalate_empty_note_raises(self):
        t = open_ticket("T-014", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        with pytest.raises(ReClearViolation, match="non-empty note"):
            blocked.escalate("")

    def test_escalate_whitespace_note_raises(self):
        t = open_ticket("T-015", "G-15-1", "Write in L0")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        with pytest.raises(ReClearViolation, match="non-empty note"):
            blocked.escalate("   ")


# ---------------------------------------------------------------------------
# Full Path D lifecycle integration test
# ---------------------------------------------------------------------------


class TestPathDLifecycle:
    def test_full_path_d_violation_then_clear(self):
        """Positive control: detect → ticket → remediate → re-evaluate → CLEARED."""
        remediated = False

        def constraint() -> bool:
            return remediated

        t = open_ticket("LIFE-001", "G-15-1", "L0 write mutation detected")
        assert t.status == ReClearStatus.PENDING

        # First re-evaluation before fix — should block
        blocked = t.re_evaluate(constraint_fn=constraint)
        assert blocked.status == ReClearStatus.BLOCKED

        # Apply remediation
        remediated = True

        # Ticket is terminal — must open a new one for second attempt
        t2 = open_ticket("LIFE-002", "G-15-1", "L0 write mutation (second attempt)")
        cleared = t2.re_evaluate(constraint_fn=constraint)
        assert cleared.status == ReClearStatus.CLEARED

    def test_full_path_d_with_escalation(self):
        """Escalation path: detect → ticket → fail re-evaluate → escalate."""
        t = open_ticket("ESC-001", "G-15-2", "Unresolvable L5 violation")
        blocked = t.re_evaluate(constraint_fn=lambda: False)
        escalated = blocked.escalate("Approved by infosec-lead: compensating control documented")
        assert escalated.status == ReClearStatus.ESCALATED
        assert escalated.ticket_id == "ESC-001"
