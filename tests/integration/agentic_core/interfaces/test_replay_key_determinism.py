"""Addendum 2.1: compute_replay_key() determinism tests."""

from __future__ import annotations

from agentic_core.interfaces.write_gateway import compute_replay_key
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_replay_key_determinism")
_emit_applies_guardrail("p0", "test_replay_key_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_key_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_replay_key_determinism", "state_snapshot")
emit_replay_key("p0", "test_replay_key_determinism")
emit_determinism_digest("p0", "test_replay_key_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestComputeReplayKey:
    def test_identical_inputs_produce_same_key(self):
        k1 = compute_replay_key("ph1", ["tool_a", "tool_b"], "stdout_digest", "diff_hash")
        k2 = compute_replay_key("ph1", ["tool_a", "tool_b"], "stdout_digest", "diff_hash")
        assert k1 == k2

    def test_tool_call_order_independent(self):
        """Sorted tool_calls — order must not matter."""
        k1 = compute_replay_key("ph1", ["tool_b", "tool_a"], "stdout", "diff")
        k2 = compute_replay_key("ph1", ["tool_a", "tool_b"], "stdout", "diff")
        assert k1 == k2

    def test_different_plan_hash_different_key(self):
        k1 = compute_replay_key("plan_A", ["t1"], "stdout", "diff")
        k2 = compute_replay_key("plan_B", ["t1"], "stdout", "diff")
        assert k1 != k2

    def test_different_stdout_different_key(self):
        k1 = compute_replay_key("ph", ["t1"], "stdout_A", "diff")
        k2 = compute_replay_key("ph", ["t1"], "stdout_B", "diff")
        assert k1 != k2

    def test_different_state_diff_different_key(self):
        k1 = compute_replay_key("ph", ["t1"], "stdout", "diff_A")
        k2 = compute_replay_key("ph", ["t1"], "stdout", "diff_B")
        assert k1 != k2

    def test_returns_64_char_hex(self):
        k = compute_replay_key("ph", ["t"], "out", "diff")
        assert len(k) == 64
        assert all(c in "0123456789abcdef" for c in k)

    def test_empty_tool_calls_deterministic(self):
        k1 = compute_replay_key("ph", [], "out", "diff")
        k2 = compute_replay_key("ph", [], "out", "diff")
        assert k1 == k2

    def test_negative_wrong_diff_produces_different_key(self):
        """Negative: mutating any field must change the key."""
        k_correct = compute_replay_key("plan", ["t1"], "stdout", "real_diff")
        k_tampered = compute_replay_key("plan", ["t1"], "stdout", "fake_diff")
        assert k_correct != k_tampered
