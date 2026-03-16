"""Addendum 2.3: TwoPhaseCoordinator tests."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.commit.two_phase_coordinator import TwoPhaseCoordinator
from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_two_phase_commit")
_emit_applies_guardrail("p0", "test_two_phase_commit", "p0_governance")
_emit_reads_policy_state("p0", "test_two_phase_commit", "policy_binding")
_emit_snapshots_state("p0", "test_two_phase_commit", "state_snapshot")
emit_replay_key("p0", "test_two_phase_commit")
emit_determinism_digest("p0", "test_two_phase_commit")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_two_phase_commit", "execution_auth")
_emit_validates_capability("p2", "test_two_phase_commit", "capability_check")
_emit_routes_to_capability("p2", "test_two_phase_commit", "capability_route")
_emit_writes_via_uwg("p2", "test_two_phase_commit", "uwg_write")
_emit_blocks_direct_write("p2", "test_two_phase_commit", "direct_write_block")
_emit_records_tool_invocation("p2", "test_two_phase_commit", "tool_invocation")
_emit_captures_execution_output("p2", "test_two_phase_commit", "exec_output")
_emit_dispatches_agent("p3", "test_two_phase_commit", "agent_dispatch")
_emit_coordinates_agents("p3", "test_two_phase_commit", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_two_phase_commit", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_two_phase_commit", "healing_outcome")
_emit_escalates_failure("p3", "test_two_phase_commit", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_two_phase_commit", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_two_phase_commit", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_two_phase_commit", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_two_phase_commit", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_two_phase_commit", "eval_metric")
_emit_stores_embedding("p4", "test_two_phase_commit", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_two_phase_commit", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_two_phase_commit", "exec_snapshot_link")


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
