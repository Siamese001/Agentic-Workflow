"""Tests for HealingSuccessRateStore (Phase 1)."""

from __future__ import annotations

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_healing_success_rate_store", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_success_rate_store", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_success_rate_store", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_success_rate_store", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_success_rate_store", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_success_rate_store", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_success_rate_store", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_success_rate_store", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_success_rate_store", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_success_rate_store", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_success_rate_store", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_success_rate_store", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_success_rate_store", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_success_rate_store", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_success_rate_store", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_success_rate_store", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_success_rate_store", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_success_rate_store", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_success_rate_store", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_success_rate_store", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
#  # MOVED: from system_learning.engines.healing_success_rate_store import (
    _EMA_ALPHA,
    _MIN_SAMPLE_SIZE,
    _NEUTRAL_PRIOR,
    HealingSuccessRateStore,
    get_default_store,
    reset_default_store,
)

# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_success_rate_store", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_success_rate_store", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_success_rate_store", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_success_rate_store", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_success_rate_store", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_success_rate_store", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_success_rate_store", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_success_rate_store", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_success_rate_store", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_success_rate_store", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_success_rate_store", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_success_rate_store", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_success_rate_store", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_success_rate_store", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_success_rate_store", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_success_rate_store", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_success_rate_store", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_success_rate_store", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_success_rate_store", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_success_rate_store", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_success_rate_store", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_success_rate_store", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_success_rate_store", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_success_rate_store")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_success_rate_store", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_success_rate_store", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_success_rate_store", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_healing_success_rate_store", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_success_rate_store", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_success_rate_store", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_success_rate_store", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_healing_success_rate_store", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_success_rate_store", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_success_rate_store", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_success_rate_store", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_success_rate_store", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_success_rate_store", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_success_rate_store", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_success_rate_store", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_success_rate_store", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_success_rate_store", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_success_rate_store", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_success_rate_store", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_success_rate_store", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_success_rate_store", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_success_rate_store", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_success_rate_store", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_success_rate_store")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_success_rate_store", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_success_rate_store")
# REMOVED: emit_determinism_digest("p0", "test_healing_success_rate_store")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def test_store_initial_state() -> None:
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from system_learning.engines.healing_success_rate_store import (
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
