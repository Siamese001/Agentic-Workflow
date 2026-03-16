"""Tests for HealingSuccessRateStore (Phase 1)."""

from __future__ import annotations

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

_emit_authorize_and_execute("p2", "test_healing_success_rate_store", "execution_auth")
_emit_validates_capability("p2", "test_healing_success_rate_store", "capability_check")
_emit_routes_to_capability("p2", "test_healing_success_rate_store", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_success_rate_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_success_rate_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_success_rate_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_success_rate_store", "exec_output")
_emit_dispatches_agent("p3", "test_healing_success_rate_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_success_rate_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_success_rate_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_success_rate_store", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_success_rate_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_success_rate_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_success_rate_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_success_rate_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_success_rate_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_success_rate_store", "eval_metric")
_emit_stores_embedding("p4", "test_healing_success_rate_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_success_rate_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_success_rate_store", "exec_snapshot_link")
from system_learning.engines.healing_success_rate_store import (
    _EMA_ALPHA,
    _MIN_SAMPLE_SIZE,
    _NEUTRAL_PRIOR,
    HealingSuccessRateStore,
    get_default_store,
    reset_default_store,
)

_emit_records_execution_trace("p0", "evidence", "test_healing_success_rate_store")
_emit_applies_guardrail("p0", "test_healing_success_rate_store", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_success_rate_store", "policy_binding")
_emit_snapshots_state("p0", "test_healing_success_rate_store", "state_snapshot")
emit_replay_key("p0", "test_healing_success_rate_store")
emit_determinism_digest("p0", "test_healing_success_rate_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def test_store_initial_state() -> None:
    """Store starts empty and returns neutral prior."""
    store = HealingSuccessRateStore()
    assert store.get_prior("any_sig") == _NEUTRAL_PRIOR
    assert store.get_all() == {}
    assert store.get_counts() == {}


def test_record_outcome_cumulative_average() -> None:
    """First few outcomes use cumulative average."""
    store = HealingSuccessRateStore()

    # First outcome: success
    store.record_outcome("sig1", True)
    assert store.get_prior("sig1") == _NEUTRAL_PRIOR  # < min samples
    assert store.get_counts()["sig1"] == 1

    # Second outcome: success
    store.record_outcome("sig1", True)
    assert store.get_prior("sig1") == _NEUTRAL_PRIOR  # < min samples
    assert store.get_counts()["sig1"] == 2

    # Third outcome: success
    store.record_outcome("sig1", True)
    assert store.get_prior("sig1") == _NEUTRAL_PRIOR  # < min samples
    assert store.get_counts()["sig1"] == 3

    # Fourth outcome: success
    store.record_outcome("sig1", True)
    assert store.get_prior("sig1") == _NEUTRAL_PRIOR  # < min samples
    assert store.get_counts()["sig1"] == 4

    # Fifth outcome: success - now at min sample size
    store.record_outcome("sig1", True)
    assert store.get_prior("sig1") == 1.0  # 5/5 success rate
    assert store.get_counts()["sig1"] == 5


def test_record_outcome_ema_after_min_samples() -> None:
    """After min samples, store uses EMA."""
    store = HealingSuccessRateStore()

    # Add min samples of all successes
    for _ in range(_MIN_SAMPLE_SIZE):
        store.record_outcome("sig1", True)

    assert store.get_prior("sig1") == 1.0

    # Add a failure - should apply EMA
    store.record_outcome("sig1", False)
    expected = (1.0 - _EMA_ALPHA) * 1.0 + _EMA_ALPHA * 0.0
    assert abs(store.get_prior("sig1") - expected) < 1e-6


def test_record_outcome_precision() -> None:
    """All stored values are rounded to 6 decimals."""
    store = HealingSuccessRateStore()

    # Add min samples to get real rate
    for _ in range(_MIN_SAMPLE_SIZE):
        store.record_outcome("sig1", True)

    # Add a failure to get non-terminating decimal
    store.record_outcome("sig1", False)

    rate = store.get_prior("sig1")
    assert len(str(rate).split(".")[-1]) <= 6  # Max 6 decimal places


def test_export_import_state() -> None:
    """Store can export and import state for replay."""
    store1 = HealingSuccessRateStore()

    store1.record_outcome("sig1", True)
    store1.record_outcome("sig1", False)
    store1.record_outcome("sig2", True)

    state = store1.export_state()
    assert "rates" in state
    assert "counts" in state
    assert "owner_pid" in state

    # Create new store and import state
    store2 = HealingSuccessRateStore()
    store2.import_state(state)

    assert store2.get_all() == store1.get_all()
    assert store2.get_counts() == store1.get_counts()


def test_store_state_hash() -> None:
    """State hash is deterministic."""
    store = HealingSuccessRateStore()

    store.record_outcome("sig1", True)
    store.record_outcome("sig2", False)

    hash1 = store.store_state_hash()
    hash2 = store.store_state_hash()

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex


def test_reset() -> None:
    """Reset clears all state."""
    store = HealingSuccessRateStore()

    store.record_outcome("sig1", True)
    assert store.get_all() != {}

    store.reset()
    assert store.get_all() == {}
    assert store.get_counts() == {}


def test_default_store_singleton() -> None:
    """Default store is a singleton."""
    reset_default_store()

    store1 = get_default_store()
    store2 = get_default_store()

    assert store1 is store2

    reset_default_store()
    store3 = get_default_store()

    assert store1 is not store3


def test_pid_guard() -> None:
    """Store operations are no-ops after fork."""
    store = HealingSuccessRateStore()
    original_pid = store._owner_pid

    # Simulate fork by changing owner_pid
    store._owner_pid = 99999

    # Operations should be no-ops (no exception, just no change)
    store.record_outcome("sig1", True)
    assert store.get_counts() == {}

    # Restore correct PID
    store._owner_pid = original_pid
    store.record_outcome("sig1", True)
    assert store.get_counts()["sig1"] == 1
