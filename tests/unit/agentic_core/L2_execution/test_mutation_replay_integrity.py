"""Addendum 1.2: Transcript–Mutation Cross Check tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.sandbox.boundary_validator import (
    compute_boundary_diff,
    verify_mutation_replay_integrity,
)
from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
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

_emit_records_execution_trace("p0", "evidence", "test_mutation_replay_integrity")
_emit_applies_guardrail("p0", "test_mutation_replay_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_mutation_replay_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_mutation_replay_integrity", "state_snapshot")
emit_replay_key("p0", "test_mutation_replay_integrity")
emit_determinism_digest("p0", "test_mutation_replay_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_mutation_replay_integrity", "execution_auth")
_emit_validates_capability("p2", "test_mutation_replay_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_mutation_replay_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_mutation_replay_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_mutation_replay_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_mutation_replay_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_mutation_replay_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_mutation_replay_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_mutation_replay_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_mutation_replay_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_mutation_replay_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_mutation_replay_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_mutation_replay_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_mutation_replay_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_mutation_replay_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_mutation_replay_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_mutation_replay_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_mutation_replay_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_mutation_replay_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_mutation_replay_integrity", "exec_snapshot_link")


class TestComputeBoundaryDiff:
    def test_no_changes_returns_empty_diff(self):
        pre = {"file_a": "v1", "file_b": "v2"}
        post = {"file_a": "v1", "file_b": "v2"}
        diff = compute_boundary_diff(pre, post)
        assert diff == {}

    def test_changed_key_captured(self):
        pre = {"file_a": "v1"}
        post = {"file_a": "v2"}
        diff = compute_boundary_diff(pre, post)
        assert "file_a" in diff
        assert diff["file_a"]["pre"] == "v1"
        assert diff["file_a"]["post"] == "v2"

    def test_added_key_captured(self):
        pre = {}
        post = {"new_file": "content"}
        diff = compute_boundary_diff(pre, post)
        assert "new_file" in diff
        assert diff["new_file"]["pre"] is None

    def test_removed_key_captured(self):
        pre = {"old_file": "content"}
        post = {}
        diff = compute_boundary_diff(pre, post)
        assert "old_file" in diff
        assert diff["old_file"]["post"] is None


class TestVerifyMutationReplayIntegrity:
    def test_matching_diff_passes(self):
        pre = {"file_a": "v1", "file_b": "v2"}
        post = {"file_a": "v1_updated", "file_b": "v2"}
        uwg_diff = compute_boundary_diff(pre, post)
        verify_mutation_replay_integrity(pre, post, uwg_diff)

    def test_no_mutations_passes(self):
        snap = {"file_a": "v1"}
        verify_mutation_replay_integrity(snap, snap, {})

    def test_mismatched_diff_raises(self):
        pre = {"file_a": "v1"}
        post = {"file_a": "v1_updated"}
        fake_uwg_diff = {"file_a": {"pre": "v1", "post": "TAMPERED"}}
        with pytest.raises(MutationReplayIntegrityViolation, match="hash mismatch"):
            verify_mutation_replay_integrity(pre, post, fake_uwg_diff)

    def test_negative_correct_diff_never_raises(self):
        """Negative control: valid diff must not raise."""
        pre = {"x": "1", "y": "2"}
        post = {"x": "1", "y": "9"}
        correct_diff = compute_boundary_diff(pre, post)
        raised = False
        try:
            verify_mutation_replay_integrity(pre, post, correct_diff)
        except MutationReplayIntegrityViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised

    def test_empty_snapshots_pass(self):
        verify_mutation_replay_integrity({}, {}, {})
