"""Addendum 2.3: TwoPhaseCoordinator tests."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.commit.two_phase_coordinator import TwoPhaseCoordinator
from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_two_phase_commit", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_two_phase_commit", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_two_phase_commit", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_two_phase_commit", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_two_phase_commit", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_two_phase_commit", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_two_phase_commit", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_two_phase_commit", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_two_phase_commit", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_two_phase_commit", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_two_phase_commit", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_two_phase_commit", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_two_phase_commit", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_two_phase_commit", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_two_phase_commit", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_two_phase_commit", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_two_phase_commit", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_two_phase_commit", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_two_phase_commit", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_two_phase_commit", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_two_phase_commit", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_two_phase_commit", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_two_phase_commit", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_two_phase_commit")
# REMOVED: _emit_applies_guardrail("p0", "test_two_phase_commit", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_two_phase_commit", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_two_phase_commit", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_two_phase_commit", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_two_phase_commit", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_two_phase_commit", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_two_phase_commit", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_two_phase_commit", "write_through")
# REMOVED: _emit_writes_through("p1", "test_two_phase_commit", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_two_phase_commit", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_two_phase_commit", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_two_phase_commit", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_two_phase_commit", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_two_phase_commit", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_two_phase_commit", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_two_phase_commit", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_two_phase_commit", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_two_phase_commit", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_two_phase_commit", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_two_phase_commit", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_two_phase_commit", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_two_phase_commit", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_two_phase_commit", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_two_phase_commit")
# REMOVED: _emit_gated_by_confidence("p1", "test_two_phase_commit", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_two_phase_commit")
# REMOVED: emit_determinism_digest("p0", "test_two_phase_commit")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_two_phase_commit", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_two_phase_commit", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_two_phase_commit", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_two_phase_commit", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_two_phase_commit", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_two_phase_commit", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_two_phase_commit", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_two_phase_commit", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_two_phase_commit", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_two_phase_commit", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_two_phase_commit", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_two_phase_commit", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_two_phase_commit", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_two_phase_commit", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_two_phase_commit", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_two_phase_commit", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_two_phase_commit", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_two_phase_commit", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_two_phase_commit", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_two_phase_commit", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestTwoPhaseCoordinator:
    def test_both_acks_succeed(self):
        coordinator = TwoPhaseCoordinator()
        r_calls, l_calls = [], []
        r, l = coordinator.execute_commit(
            resource_write=lambda: r_calls.append(1) or "resource_ok",
            ledger_write=lambda: l_calls.append(1) or "ledger_ok",
        )
        assert r == "resource_ok"
        assert l == "ledger_ok"
        assert len(r_calls) == 1
        assert len(l_calls) == 1

    def test_resource_failure_raises_phase1(self):
        coordinator = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure, match="Phase 1"):
            coordinator.execute_commit(
                resource_write=lambda: (_ for _ in ()).throw(RuntimeError("disk full")),
                ledger_write=lambda: "ok",
            )

    def test_ledger_failure_raises_phase2(self):
        coordinator = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure, match="Phase 2"):
            coordinator.execute_commit(
                resource_write=lambda: "ok",
                ledger_write=lambda: (_ for _ in ()).throw(RuntimeError("ledger locked")),
            )

    def test_ledger_not_called_if_resource_fails(self):
        coordinator = TwoPhaseCoordinator()
        ledger_calls = []
        with pytest.raises(MutationCommitFailure):
            coordinator.execute_commit(
                resource_write=lambda: (_ for _ in ()).throw(RuntimeError("fail")),
                ledger_write=lambda: ledger_calls.append(1) or "ok",
            )
        assert len(ledger_calls) == 0, "Ledger must not be called when resource write fails"

    def test_safe_commit_returns_success_dict(self):
        coordinator = TwoPhaseCoordinator()
        result = coordinator.safe_commit(
            resource_write=lambda: "r",
            ledger_write=lambda: "l",
        )
        assert result["success"] is True
        assert result["resource_result"] == "r"
        assert result["ledger_result"] == "l"

    def test_safe_commit_returns_failure_dict(self):
        coordinator = TwoPhaseCoordinator()
        result = coordinator.safe_commit(
            resource_write=lambda: (_ for _ in ()).throw(RuntimeError("fail")),
            ledger_write=lambda: "l",
        )
        assert result["success"] is False
        assert "error" in result

    def test_negative_both_ok_no_exception(self):
        """Negative control: successful 2PC must never raise."""
        coordinator = TwoPhaseCoordinator()
        raised = False
        try:
            coordinator.execute_commit(
                resource_write=lambda: "ok",
                ledger_write=lambda: "ok",
            )
        except MutationCommitFailure:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
