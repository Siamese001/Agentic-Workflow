"""
Unit tests for Meta-Learning Bus - queue-backed deterministic change conduit.
"""

import pytest

from agentic_core.L0_routing.meta_control.meta_learning_bus import (
    MetaLearningBus,
    MetaLearningChangePackage,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_bus", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_bus", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_bus", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_bus", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_bus", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_bus", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_bus", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_bus", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_bus", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_bus", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_bus", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_bus", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_bus", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_bus", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_bus", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_bus", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_bus", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_bus", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_bus", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_bus", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_bus", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_bus", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_bus", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_bus")
_emit_applies_guardrail("p0", "test_meta_learning_bus", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_bus", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_bus", "state_snapshot")
_emit_pulls_context("p1", "test_meta_learning_bus", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_bus", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_learning_bus", "write_through")
_emit_writes_through("p1", "test_meta_learning_bus", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_learning_bus", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_bus", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_bus", "routing_commit")
emit_replay_key("p0", "test_meta_learning_bus")
emit_determinism_digest("p0", "test_meta_learning_bus")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_bus", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_bus", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_bus", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_bus", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_bus", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_bus", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_bus", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_bus", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_bus", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_bus", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_bus", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_bus", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_bus", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_bus", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_bus", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_bus", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_bus", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_bus", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_bus", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_bus", "exec_snapshot_link")


@pytest.mark.unit
class TestMetaLearningChangePackage:
    """Test MetaLearningChangePackage dataclass and hashing."""

    def test_create_package_with_deterministic_hash(self):
        """Test package creation with deterministic hash computation."""
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value", "number": 42}
        )

        assert pkg.trace_id == "trace123"
        assert pkg.kind == "test_change"
        assert pkg.payload == {"key": "value", "number": 42}
        assert pkg.package_hash is not None
        assert len(pkg.package_hash) == 64  # SHA-256 hex length

    def test_package_hash_deterministic_across_identical_inputs(self):
        """Test package hash is deterministic across identical inputs."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value", "number": 42}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace456",  # Different trace_id shouldn't affect hash
            kind="test_change",
            payload={"key": "value", "number": 42},
        )

        # Hash should be same for same kind+payload regardless of trace_id
        assert pkg1.package_hash == pkg2.package_hash

    def test_package_hash_different_for_different_payloads(self):
        """Test package hash differs for different payloads."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value1"}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value2"}
        )

        assert pkg1.package_hash != pkg2.package_hash

    def test_package_hash_different_for_different_kinds(self):
        """Test package hash differs for different kinds."""
        payload = {"key": "value"}

        pkg1 = MetaLearningChangePackage.create(trace_id="trace123", kind="kind1", payload=payload)

        pkg2 = MetaLearningChangePackage.create(trace_id="trace123", kind="kind2", payload=payload)

        assert pkg1.package_hash != pkg2.package_hash

    def test_package_hash_ignores_payload_key_order(self):
        """Test package hash ignores payload key order (canonical JSON)."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"z": 1, "a": 2, "m": 3}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"a": 2, "m": 3, "z": 1}
        )

        assert pkg1.package_hash == pkg2.package_hash

    def test_package_immutability(self):
        """Test package is immutable."""
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value"}
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            pkg.trace_id = "changed"

        with pytest.raises(AttributeError):
            pkg.kind = "changed"

        with pytest.raises(AttributeError):
            pkg.payload = {"changed": "value"}


@pytest.mark.unit
class TestMetaLearningBus:
    """Test MetaLearningBus queue operations."""

    def test_bus_initialization_empty(self):
        """Test bus initializes with empty queue."""
        bus = MetaLearningBus()

        assert bus.size() == 0
        assert bus.dequeue() is None

    def test_enqueue_and_dequeue_single_package(self):
        """Test enqueue and dequeue of single package."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value"}
        )

        bus.enqueue(pkg)
        assert bus.size() == 1

        dequeued = bus.dequeue()
        assert dequeued == pkg
        assert bus.size() == 0

    def test_fifo_ordering_preserved(self):
        """Test FIFO ordering is preserved."""
        bus = MetaLearningBus()

        pkg1 = MetaLearningChangePackage.create("trace1", "kind1", {"seq": 1})
        pkg2 = MetaLearningChangePackage.create("trace2", "kind2", {"seq": 2})
        pkg3 = MetaLearningChangePackage.create("trace3", "kind3", {"seq": 3})

        # Enqueue in order
        bus.enqueue(pkg1)
        bus.enqueue(pkg2)
        bus.enqueue(pkg3)

        # Should dequeue in same order
        assert bus.dequeue() == pkg1
        assert bus.dequeue() == pkg2
        assert bus.dequeue() == pkg3
        assert bus.dequeue() is None

    def test_dequeue_returns_none_when_empty(self):
        """Test dequeue returns None when queue is empty."""
        bus = MetaLearningBus()

        assert bus.dequeue() is None

        # Add and remove a package
        pkg = MetaLearningChangePackage.create("trace", "kind", {})
        bus.enqueue(pkg)
        bus.dequeue()

        # Should still return None
        assert bus.dequeue() is None

    def test_size_tracking(self):
        """Test size tracking works correctly."""
        bus = MetaLearningBus()

        assert bus.size() == 0

        pkg = MetaLearningChangePackage.create("trace", "kind", {})
        bus.enqueue(pkg)
        assert bus.size() == 1

        bus.enqueue(pkg)
        assert bus.size() == 2

        bus.dequeue()
        assert bus.size() == 1

        bus.dequeue()
        assert bus.size() == 0

    def test_apply_next_calls_injected_function(self):
        """Test apply_next calls injected apply_fn exactly once."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create("trace123", "test_change", {"key": "value"})

        # Track calls to apply_fn
        calls = []

        def mock_apply_fn(package):
            calls.append(package)
            return "result_" + package.trace_id

        bus.enqueue(pkg)

        result = bus.apply_next(apply_fn=mock_apply_fn)

        assert result is not None
        returned_pkg, returned_result = result
        assert returned_pkg == pkg
        assert returned_result == "result_trace123"
        assert len(calls) == 1
        assert calls[0] == pkg

    def test_apply_next_returns_deterministic_tuple(self):
        """Test apply_next returns deterministic tuple."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create("trace123", "test_change", {"key": "value"})

        def mock_apply_fn(package):
            return {"applied": True, "trace": package.trace_id}

        bus.enqueue(pkg)

        result1 = bus.apply_next(apply_fn=mock_apply_fn)
        result2 = bus.apply_next(apply_fn=mock_apply_fn)

        # First call should return tuple, second should return None
        assert result1 is not None
        assert result1[0] == pkg
        assert result1[1] == {"applied": True, "trace": "trace123"}

        assert result2 is None

    def test_apply_next_empty_queue_does_not_call_apply_fn(self):
        """Test apply_next returns None and does not call apply_fn when queue empty."""
        bus = MetaLearningBus()

        calls = []

        def mock_apply_fn(package):
            calls.append(package)
            return "result"

        result = bus.apply_next(apply_fn=mock_apply_fn)

        assert result is None
        assert len(calls) == 0

    def test_apply_next_multiple_packages(self):
        """Test apply_next with multiple packages."""
        bus = MetaLearningBus()

        pkg1 = MetaLearningChangePackage.create("trace1", "kind1", {"seq": 1})
        pkg2 = MetaLearningChangePackage.create("trace2", "kind2", {"seq": 2})

        results = []

        def mock_apply_fn(package):
            results.append(package.trace_id)
            return f"processed_{package.trace_id}"

        bus.enqueue(pkg1)
        bus.enqueue(pkg2)

        # Apply first package
        result1 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result1 is not None
        assert result1[0] == pkg1
        assert result1[1] == "processed_trace1"

        # Apply second package
        result2 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result2 is not None
        assert result2[0] == pkg2
        assert result2[1] == "processed_trace2"

        # No more packages
        result3 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result3 is None

        # Verify apply_fn was called exactly twice
        assert results == ["trace1", "trace2"]
