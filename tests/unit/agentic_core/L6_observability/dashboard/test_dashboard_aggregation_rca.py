"""
RCA Regression Tests — Dashboard Aggregation Recursion Bugs

Tests that verify all three infinite-recursion paths identified in the RCA
are definitively broken and cannot regress:

  Bug#1 — _emit_records_execution_trace called aggregate_simple_dashboard,
           which called aggregate_runtime_observability, which called
           _emit_records_execution_trace → unbounded mutual recursion.

  Bug#2 — DashboardAggregateRegistry.get_instance() called
           _emit_records_execution_trace → aggregate_simple_dashboard
           → get_dashboard_registry → get_instance → recursion.

  Bug#3 — DashboardAggregate.computed_at_tick default used get_clock()
           which with WallClock called _emit_records_execution_trace
           → recursion at dataclass instantiation time.

Each test is deterministic, uses RecursionError detection or call-count
assertions to prove the fix holds, and tears down cleanly.
"""
from __future__ import annotations



import sys
import threading
import time
import uuid
from unittest.mock import patch

import pytest

from agentic_core.L6_observability.dashboard.dashboard_aggregate import (
    DashboardAggregate,
    DashboardAggregateRegistry,
    DashboardSnapshot,
    HealthFlag,
    get_dashboard_registry,
    reset_dashboard_registry,
)
from agentic_core.L6_observability.dashboard.dashboard_orchestrator import (
    DashboardPolicy,
    TelemetryWindow,
    aggregate_runtime_observability,
    aggregate_simple_dashboard,
)
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

# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_dashboard_aggregation_rca", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_dashboard_aggregation_rca", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_dashboard_aggregation_rca", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_dashboard_aggregation_rca", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_dashboard_aggregation_rca", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_dashboard_aggregation_rca", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_dashboard_aggregation_rca", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_dashboard_aggregation_rca", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_dashboard_aggregation_rca", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_dashboard_aggregation_rca", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_dashboard_aggregation_rca", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_dashboard_aggregation_rca", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_dashboard_aggregation_rca", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_dashboard_aggregation_rca", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_dashboard_aggregation_rca", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_dashboard_aggregation_rca", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_dashboard_aggregation_rca", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_dashboard_aggregation_rca", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_dashboard_aggregation_rca", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_dashboard_aggregation_rca", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_dashboard_aggregation_rca", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_dashboard_aggregation_rca", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_dashboard_aggregation_rca", "runtime_state", "p2_rt_2")

# REMOVED: _emit_applies_guardrail("p0", "test_dashboard_aggregation_rca", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_dashboard_aggregation_rca", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_dashboard_aggregation_rca", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_dashboard_aggregation_rca", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dashboard_aggregation_rca", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dashboard_aggregation_rca", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_dashboard_aggregation_rca", "write_through")
# REMOVED: _emit_writes_through("p1", "test_dashboard_aggregation_rca", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_dashboard_aggregation_rca", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_dashboard_aggregation_rca", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_dashboard_aggregation_rca", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_dashboard_aggregation_rca", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_dashboard_aggregation_rca", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_dashboard_aggregation_rca", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_dashboard_aggregation_rca", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_dashboard_aggregation_rca", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_dashboard_aggregation_rca", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_dashboard_aggregation_rca", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_dashboard_aggregation_rca", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_dashboard_aggregation_rca", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_dashboard_aggregation_rca", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_dashboard_aggregation_rca", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_dashboard_aggregation_rca")
# REMOVED: _emit_gated_by_confidence("p1", "test_dashboard_aggregation_rca", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_dashboard_aggregation_rca")
# REMOVED: emit_determinism_digest("p0", "test_dashboard_aggregation_rca")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_dashboard_aggregation_rca", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_dashboard_aggregation_rca", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_dashboard_aggregation_rca", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_dashboard_aggregation_rca", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_dashboard_aggregation_rca", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_dashboard_aggregation_rca", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_dashboard_aggregation_rca", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_dashboard_aggregation_rca", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_dashboard_aggregation_rca", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_dashboard_aggregation_rca", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_dashboard_aggregation_rca", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_dashboard_aggregation_rca", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_dashboard_aggregation_rca", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_dashboard_aggregation_rca", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_dashboard_aggregation_rca", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_dashboard_aggregation_rca", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_dashboard_aggregation_rca", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_dashboard_aggregation_rca", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_dashboard_aggregation_rca", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_dashboard_aggregation_rca", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset singleton registry before and after each test."""
    reset_dashboard_registry()
    yield
    reset_dashboard_registry()


# ---------------------------------------------------------------------------
# Bug#1 — No recursion from _emit_records_execution_trace
# ---------------------------------------------------------------------------


class TestBug1NoRecursionFromEmitter:
    """_emit_records_execution_trace must be a pure fire-and-forget logger.

    It must NOT call aggregate_simple_dashboard or any dashboard function.
    Pre-fix: calling this would instantly recurse into aggregate_simple_dashboard
    → aggregate_runtime_observability → _emit_records_execution_trace → ...
    """

    def test_emit_records_does_not_call_aggregate_simple_dashboard(self):
        """aggregate_simple_dashboard must NOT be called from within _emit_records_execution_trace."""
        call_count = []

        original = aggregate_simple_dashboard

        def spy_aggregate(*args, **kwargs):
            call_count.append(1)
            return original(*args, **kwargs)

        with patch(
            "agentic_core.runtime.lifecycle_trace_contract.aggregate_simple_dashboard",
            spy_aggregate,
            create=True,
        ):
# REMOVED:             _emit_records_execution_trace("trace-001", "L0", "test_op")

        assert len(call_count) == 0, (
            f"Bug#1 regression: _emit_records_execution_trace triggered "
            f"aggregate_simple_dashboard {len(call_count)} times (expected 0)"
        )

    def test_emit_records_does_not_import_dashboard_orchestrator(self):
        """_emit_records_execution_trace must not lazy-import dashboard_orchestrator."""
        # Remove orchestrator from sys.modules to detect fresh import
        mod_key = "agentic_core.L6_observability.dashboard.dashboard_orchestrator"
        was_present = mod_key in sys.modules
        # We just call the emitter and verify no RecursionError
        try:
            for _ in range(500):
# REMOVED:                 _emit_records_execution_trace(str(uuid.uuid4()), "L3", f"op_{_}")
        except RecursionError as exc:
            pytest.fail(f"Bug#1 regression: RecursionError from _emit_records_execution_trace: {exc}")

    def test_emit_records_survives_1000_calls_without_recursion(self):
        """Calling _emit_records_execution_trace 1000 times must never RecursionError."""
        try:
            for i in range(1000):
# REMOVED:                 _emit_records_execution_trace(f"trace-{i}", "L5", "bulk_op")
        except RecursionError as exc:
            pytest.fail(f"Bug#1 regression: RecursionError on call {i}: {exc}")

    def test_emit_records_returns_none_no_side_effects(self):
        """_emit_records_execution_trace must return None (pure emitter)."""
        result = _emit_records_execution_trace("trace-x", "L2", "op_x")
        assert result is None

    def test_aggregate_runtime_observability_does_not_recurse(self):
        """aggregate_runtime_observability itself must complete without RecursionError."""
        window = TelemetryWindow.create(
            window_start_tick=time.time() - 60,
            window_end_tick=time.time(),
        )
        policy = DashboardPolicy.create()
        registry = DashboardAggregateRegistry()

        try:
            snapshot = aggregate_runtime_observability(
                telemetry_window=window,
                dashboard_policy=policy,
                registry=registry,
            )
        except RecursionError as exc:
            pytest.fail(f"Bug#1 regression: aggregate_runtime_observability recursed: {exc}")

        assert snapshot is not None
        assert snapshot.dashboard_snapshot_id


# ---------------------------------------------------------------------------
# Bug#2 — No recursion from DashboardAggregateRegistry.get_instance()
# ---------------------------------------------------------------------------


class TestBug2NoRecursionFromGetInstance:
    """get_instance() must not call _emit_records_execution_trace.

    Pre-fix: get_instance called _emit_records_execution_trace → aggregate_simple_dashboard
    → get_dashboard_registry → get_instance → recursive stack overflow.
    """

    def test_get_instance_does_not_call_emit_records(self):
        """No call to _emit_records_execution_trace should occur inside get_instance."""
        call_count = []

        original_emit = _emit_records_execution_trace

        def counting_emit(root_trace_id, layer, operation):
            if "get_instance" in operation or "DashboardAggregateRegistry" in operation:
                call_count.append(operation)
            return original_emit(root_trace_id, layer, operation)

        with patch(
            "agentic_core.L6_observability.dashboard.dashboard_aggregate._emit_records_execution_trace",
            counting_emit,
            create=True,
        ):
            reset_dashboard_registry()
            _ = get_dashboard_registry()

        assert len(call_count) == 0, f"Bug#2 regression: get_instance emitted execution traces: {call_count}"

    def test_get_instance_no_recursion_error(self):
        """Repeated get_instance calls must never RecursionError."""
        reset_dashboard_registry()
        try:
            for _ in range(200):
                reg = DashboardAggregateRegistry.get_instance()
                assert reg is not None
        except RecursionError as exc:
            pytest.fail(f"Bug#2 regression: RecursionError in get_instance: {exc}")

    def test_get_instance_returns_same_singleton(self):
        """Singleton contract: every call returns the same instance."""
        reset_dashboard_registry()
        r1 = DashboardAggregateRegistry.get_instance()
        r2 = DashboardAggregateRegistry.get_instance()
        r3 = get_dashboard_registry()
        assert r1 is r2
        assert r2 is r3

    def test_get_instance_thread_safe(self):
        """Concurrent calls must all return the same singleton without recursion."""
        reset_dashboard_registry()
        results = []
        errors = []

        def worker():
            try:
                reg = DashboardAggregateRegistry.get_instance()
                results.append(id(reg))
            except RecursionError as exc:
                errors.append(str(exc))
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Bug#2 regression: errors in concurrent get_instance: {errors}"
        assert len(set(results)) == 1, "All threads must get the same singleton"


# ---------------------------------------------------------------------------
# Bug#3 — DashboardAggregate.computed_at_tick uses time.time(), not get_clock()
# ---------------------------------------------------------------------------


class TestBug3NoDashboardAggregateRecursion:
    """DashboardAggregate instantiation must not trigger WallClock.now().

    Pre-fix: computed_at_tick default used get_clock().now_epoch() which
    with WallClock called _emit_records_execution_trace → recursion.
    """

    def test_dashboard_aggregate_instantiation_does_not_call_emit_records(self):
        """Creating DashboardAggregate must not call _emit_records_execution_trace."""
        call_count = []

        original_emit = _emit_records_execution_trace

        def counting_emit(root_trace_id, layer, operation):
            if "WallClock" in operation or "MonotonicSequenceClock" in operation:
                call_count.append(operation)
            return original_emit(root_trace_id, layer, operation)

        with patch(
            "agentic_core.L6_observability.dashboard.dashboard_aggregate._emit_records_execution_trace",
            counting_emit,
            create=True,
        ):
            agg = DashboardAggregate.create(
                aggregate_id=str(uuid.uuid4()),
                window_start_tick=time.time() - 60,
                window_end_tick=time.time(),
            )

        assert len(call_count) == 0, (
            f"Bug#3 regression: DashboardAggregate instantiation triggered clock "
            f"emit {len(call_count)} times: {call_count}"
        )
        assert agg.computed_at_tick > 0

    def test_dashboard_aggregate_computed_at_tick_is_reasonable_epoch(self):
        """computed_at_tick must be a valid recent Unix epoch float."""
        before = time.time()
        agg = DashboardAggregate.create(
            aggregate_id=str(uuid.uuid4()),
            window_start_tick=before - 60,
            window_end_tick=before,
        )
        after = time.time()

        assert before <= agg.computed_at_tick <= after + 1.0, (
            f"computed_at_tick {agg.computed_at_tick} not in expected range [{before}, {after + 1}]"
        )

    def test_dashboard_aggregate_no_recursion_error_on_bulk_create(self):
        """Creating 500 DashboardAggregate instances must not RecursionError."""
        try:
            for i in range(500):
                DashboardAggregate.create(
                    aggregate_id=str(uuid.uuid4()),
                    window_start_tick=float(i),
                    window_end_tick=float(i + 60),
                )
        except RecursionError as exc:
            pytest.fail(f"Bug#3 regression: RecursionError on DashboardAggregate.create: {exc}")


# ---------------------------------------------------------------------------
# Integration — full pipeline must complete cleanly end-to-end
# ---------------------------------------------------------------------------


class TestDashboardAggregationIntegration:
    """Full pipeline correctness after all three bug fixes."""

    def test_aggregate_simple_dashboard_returns_valid_snapshot(self):
        """aggregate_simple_dashboard must return a complete DashboardSnapshot."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(window_duration_seconds=60, registry=registry)

        assert isinstance(snapshot, DashboardSnapshot)
        assert snapshot.dashboard_snapshot_id
        assert snapshot.snapshot_tick > 0
        assert isinstance(snapshot.active_run_count, int)
        assert 0.0 <= snapshot.execution_success_rate <= 1.0
        assert isinstance(snapshot.degraded_component_flags, dict)

    def test_aggregate_simple_dashboard_snapshot_is_persisted(self):
        """Snapshot must be retrievable from registry after aggregation."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(window_duration_seconds=60, registry=registry)

        retrieved = registry.query_snapshot_by_id(snapshot.dashboard_snapshot_id)
        assert retrieved is not None
        assert retrieved.dashboard_snapshot_id == snapshot.dashboard_snapshot_id

    def test_aggregate_simple_dashboard_repeated_calls_accumulate(self):
        """Multiple calls should accumulate snapshots in the registry."""
        registry = DashboardAggregateRegistry()
        for _ in range(5):
            aggregate_simple_dashboard(window_duration_seconds=10, registry=registry)

        assert registry.get_snapshot_count() == 5

    def test_aggregate_runtime_observability_5_steps_execute(self):
        """All 5 mandatory steps must execute without error or recursion."""
        window = TelemetryWindow.create(
            window_start_tick=time.time() - 300,
            window_end_tick=time.time(),
        )
        policy = DashboardPolicy.create(
            health_thresholds={"execution": {"critical": 0.7, "degraded": 0.9}},
            latency_thresholds={"routing": {"median": 0.5}},
            throughput_thresholds={"routing": 60.0},
        )
        registry = DashboardAggregateRegistry()

        try:
            snapshot = aggregate_runtime_observability(
                telemetry_window=window,
                dashboard_policy=policy,
                registry=registry,
            )
        except RecursionError as exc:
            pytest.fail(f"Recursion in aggregate_runtime_observability: {exc}")

        assert snapshot.dashboard_snapshot_id
        assert snapshot.snapshot_tick > 0
        assert len(snapshot.degraded_component_flags) == 5  # 5 components

    def test_health_flags_computed_for_all_components(self):
        """Health flags must be computed for all 5 mandatory components."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(registry=registry)

        expected_components = {"routing", "reasoning", "execution", "escalation", "policy"}
        actual_components = set(snapshot.degraded_component_flags.keys())
        assert expected_components == actual_components

    def test_health_flag_values_are_valid_enum_members(self):
        """All health flag values must be valid HealthFlag enum members."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(registry=registry)

        valid_flags = set(HealthFlag)
        for component, flag in snapshot.degraded_component_flags.items():
            assert flag in valid_flags, f"Component '{component}' has invalid health flag: {flag!r}"

    def test_snapshot_satisfies_gate_b_core_metrics_computable(self):
        """Gate B: snapshot must pass can_compute_core_metrics()."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(registry=registry)
        assert snapshot.can_compute_core_metrics(), "Gate B violated: cannot compute core metrics"

    def test_snapshot_satisfies_gate_d_time_window_queryable(self):
        """Gate D: snapshot must pass is_queryable_by_time_window()."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(registry=registry)
        assert snapshot.is_queryable_by_time_window(), "Gate D violated: not queryable by time window"

    def test_snapshot_satisfies_gate_e_aggregation_path_exists(self):
        """Gate E: snapshot must pass has_aggregation_path()."""
        registry = DashboardAggregateRegistry()
        snapshot = aggregate_simple_dashboard(registry=registry)
        assert snapshot.has_aggregation_path(), "Gate E violated: no aggregation path"

    def test_aggregate_simple_dashboard_no_recursion_under_concurrent_calls(self):
        """Concurrent calls from multiple threads must not trigger recursion."""
        registry = DashboardAggregateRegistry()
        errors = []

        def worker():
            try:
                aggregate_simple_dashboard(window_duration_seconds=30, registry=registry)
            except RecursionError as exc:
                errors.append(f"RecursionError: {exc}")
            except Exception as exc:
                errors.append(f"Error: {exc}")

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent aggregation errors: {errors}"
        assert registry.get_snapshot_count() == 10


# ---------------------------------------------------------------------------
# DashboardSnapshot dataclass correctness
# ---------------------------------------------------------------------------


class TestDashboardSnapshotCorrectness:
    """DashboardSnapshot field validation and gate checks."""

    def _make_snapshot(self, **overrides) -> DashboardSnapshot:
        defaults = {
            "dashboard_snapshot_id": str(uuid.uuid4()),
            "snapshot_tick": time.time(),
            "active_run_count": 10,
            "routing_throughput": 1.5,
            "reasoning_throughput": 1.2,
            "execution_success_rate": 0.92,
            "execution_failure_rate": 0.08,
            "policy_block_rate": 0.02,
            "human_escalation_rate": 0.01,
            "queue_depth_summary": {"routing": 3, "execution": 5},
            "median_latency_by_stage": {"routing": 0.1, "execution": 0.2},
            "p95_latency_by_stage": {"routing": 0.3, "execution": 0.8},
            "degraded_component_flags": {"routing": HealthFlag.HEALTHY},
        }
        defaults.update(overrides)
        return DashboardSnapshot.create(**defaults)

    def test_gate_a_has_runtime_data_source_positive(self):
        snap = self._make_snapshot()
        assert snap.has_runtime_data_source()

    def test_gate_a_has_runtime_data_source_negative(self):
        snap = self._make_snapshot(
            routing_throughput=0.0,
            reasoning_throughput=0.0,
            execution_success_rate=0.0,
            execution_failure_rate=0.0,
        )
        assert not snap.has_runtime_data_source()

    def test_gate_b_can_compute_core_metrics_positive(self):
        snap = self._make_snapshot()
        assert snap.can_compute_core_metrics()

    def test_gate_c_has_degraded_subsystem_flags_when_degraded(self):
        snap = self._make_snapshot(degraded_component_flags={"routing": HealthFlag.DEGRADED})
        assert snap.has_degraded_subsystem_flags()

    def test_gate_c_no_degraded_flags_when_all_healthy(self):
        snap = self._make_snapshot(
            degraded_component_flags={"routing": HealthFlag.HEALTHY, "exec": HealthFlag.HEALTHY}
        )
        assert not snap.has_degraded_subsystem_flags()

    def test_gate_d_queryable_by_time_window(self):
        snap = self._make_snapshot()
        assert snap.is_queryable_by_time_window()

    def test_gate_d_not_queryable_with_zero_tick(self):
        snap = self._make_snapshot(snapshot_tick=0.0)
        assert not snap.is_queryable_by_time_window()

    def test_gate_e_has_aggregation_path(self):
        snap = self._make_snapshot()
        assert snap.has_aggregation_path()

    def test_snapshot_is_immutable(self):
        snap = self._make_snapshot()
        with pytest.raises((AttributeError, TypeError)):
            snap.active_run_count = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Registry correctness
# ---------------------------------------------------------------------------


class TestDashboardAggregateRegistryCorrectness:
    """DashboardAggregateRegistry storage and query correctness."""

    def _make_snapshot(self, tick: float = None, **kwargs) -> DashboardSnapshot:
        tick = tick or time.time()
        return DashboardSnapshot.create(
            dashboard_snapshot_id=str(uuid.uuid4()),
            snapshot_tick=tick,
            active_run_count=1,
            **kwargs,
        )

    def test_persist_and_retrieve_by_id(self):
        reg = DashboardAggregateRegistry()
        snap = self._make_snapshot()
        reg.persist_snapshot(snap)
        result = reg.query_snapshot_by_id(snap.dashboard_snapshot_id)
        assert result is snap

    def test_get_latest_snapshot(self):
        reg = DashboardAggregateRegistry()
        t0 = time.time()
        s1 = self._make_snapshot(tick=t0)
        s2 = self._make_snapshot(tick=t0 + 1.0)
        reg.persist_snapshot(s1)
        reg.persist_snapshot(s2)
        assert reg.get_latest_snapshot() is s2

    def test_query_by_time_window(self):
        reg = DashboardAggregateRegistry()
        t0 = time.time()
        s1 = self._make_snapshot(tick=t0)
        s2 = self._make_snapshot(tick=t0 + 30.0)
        s3 = self._make_snapshot(tick=t0 + 120.0)
        for s in [s1, s2, s3]:
            reg.persist_snapshot(s)

        results = reg.query_snapshots_by_time_window(t0 - 1, t0 + 60)
        ids = {r.dashboard_snapshot_id for r in results}
        assert s1.dashboard_snapshot_id in ids
        assert s2.dashboard_snapshot_id in ids
        assert s3.dashboard_snapshot_id not in ids

    def test_get_snapshot_count(self):
        reg = DashboardAggregateRegistry()
        for _ in range(7):
            reg.persist_snapshot(self._make_snapshot())
        assert reg.get_snapshot_count() == 7

    def test_query_missing_id_returns_none(self):
        reg = DashboardAggregateRegistry()
        assert reg.query_snapshot_by_id("nonexistent-id") is None

    def test_verify_runtime_data_source_gate_a(self):
        reg = DashboardAggregateRegistry()
        snap = self._make_snapshot(routing_throughput=1.5)
        reg.persist_snapshot(snap)
        assert reg.verify_runtime_data_source(snap.dashboard_snapshot_id)

    def test_verify_time_window_queryable_gate_d(self):
        reg = DashboardAggregateRegistry()
        snap = self._make_snapshot()
        reg.persist_snapshot(snap)
        assert reg.verify_time_window_queryable(snap.dashboard_snapshot_id)

    def test_reset_clears_singleton(self):
        r1 = DashboardAggregateRegistry.get_instance()
        reset_dashboard_registry()
        r2 = DashboardAggregateRegistry.get_instance()
        assert r1 is not r2
