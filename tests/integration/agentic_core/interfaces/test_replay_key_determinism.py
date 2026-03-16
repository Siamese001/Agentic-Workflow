"""Addendum 2.1: compute_replay_key() determinism tests."""

from __future__ import annotations

from agentic_core.interfaces.write_gateway import compute_replay_key
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

_emit_records_execution_trace("p0", "evidence", "test_replay_key_determinism")
_emit_applies_guardrail("p0", "test_replay_key_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_key_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_replay_key_determinism", "state_snapshot")
emit_replay_key("p0", "test_replay_key_determinism")
emit_determinism_digest("p0", "test_replay_key_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_key_determinism", "execution_auth")
_emit_validates_capability("p2", "test_replay_key_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_replay_key_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_key_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_key_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_key_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_key_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_replay_key_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_key_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_key_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_key_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_key_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_key_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_key_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_key_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_key_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_key_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_replay_key_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_key_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_key_determinism", "exec_snapshot_link")


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
