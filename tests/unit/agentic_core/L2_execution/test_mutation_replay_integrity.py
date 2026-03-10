"""Addendum 1.2: Transcript–Mutation Cross Check tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.sandbox.boundary_validator import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    compute_boundary_diff,
    verify_mutation_replay_integrity,
)
from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation


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
        assert True  # no-exception contract

    def test_no_mutations_passes(self):
        snap = {"file_a": "v1"}
        verify_mutation_replay_integrity(snap, snap, {})
        assert True  # no-exception contract

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
        assert True  # no-exception contract
