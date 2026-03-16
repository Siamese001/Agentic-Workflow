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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
