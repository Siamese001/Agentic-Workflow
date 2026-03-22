"""
Unit tests for L1 Cognition Telemetry Emitter - write-only, ZERO-decision component.
"""

import pytest

from agentic_core.L1_cognition.telemetry.telemetry_emitter import (
    TelemetryEmitter,
    TelemetryEvent,
    compute_event_hash,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_1")
_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_2")
_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_3")
_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_4")
_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_5")
_emit_emits_metric_event("test_telemetry_emitter", "p4obs", "metric_6")
_emit_records_incident_event("test_telemetry_emitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_telemetry_emitter", "p4obs", "anomaly")
_emit_writes_observability_log("test_telemetry_emitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_telemetry_emitter", "p4obs", "mon_state")
_emit_triggers_alert("test_telemetry_emitter", "p4obs", "alert")
_emit_links_incident_trace("test_telemetry_emitter", "p4obs", "trace_link")
_emit_captures_pattern("test_telemetry_emitter", "p3lm", "pattern")
_emit_records_learning_event("test_telemetry_emitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_telemetry_emitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_telemetry_emitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_telemetry_emitter", "p3lm", "routing")
_emit_improves_agent_policy("test_telemetry_emitter", "p3lm", "policy")
_emit_stores_learning_state("test_telemetry_emitter", "p3lm", "state")
_emit_records_execution_trace("test_telemetry_emitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_telemetry_emitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_telemetry_emitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_telemetry_emitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_telemetry_emitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_telemetry_emitter", "env_read", "p2_env_1")
_emit_reads_environ("test_telemetry_emitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_telemetry_emitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_telemetry_emitter", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_telemetry_emitter")
_emit_applies_guardrail("p0", "test_telemetry_emitter", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_emitter", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_emitter", "state_snapshot")
_emit_pulls_context("p1", "test_telemetry_emitter", "context_pull")
_emit_pulls_context("p1", "test_telemetry_emitter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_telemetry_emitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_telemetry_emitter", "uwg_term_secondary")
_emit_writes_through("p1", "test_telemetry_emitter", "write_through")
_emit_writes_through("p1", "test_telemetry_emitter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_telemetry_emitter", "safety_validation")
_emit_invokes_eval("p1", "test_telemetry_emitter", "eval_call")
_emit_proposal_commits_routing("p1", "test_telemetry_emitter", "routing_commit")
_emit_escalates_to_human("p1", "test_telemetry_emitter", "human_escalation")
_emit_routes_through("p1", "test_telemetry_emitter", "route_through")
_emit_checks_agent_registry("p1", "test_telemetry_emitter", "agent_registry")
_emit_validates_agent_capability("p1", "test_telemetry_emitter", "capability")
_emit_dispatches_execution_plan("p1", "test_telemetry_emitter", "exec_plan")
_emit_agent_executes_agent("p1", "test_telemetry_emitter", "sub_agent")
_emit_routes_to_agent("p1", "test_telemetry_emitter", "target_agent")
_emit_verifies_policy("p1", "test_telemetry_emitter", "policy_check")
_emit_observes_runtime_state("p1", "test_telemetry_emitter", "runtime_state")
_emit_verifies_boundary("p1", "test_telemetry_emitter", "boundary_check")
_emit_transcripts_response("p1", "test_telemetry_emitter", "transcript")
_emit_hard_fails_untranscripted("p1", "test_telemetry_emitter")
_emit_gated_by_confidence("p1", "test_telemetry_emitter", "confidence_gate")
emit_replay_key("p0", "test_telemetry_emitter")
emit_determinism_digest("p0", "test_telemetry_emitter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_telemetry_emitter", "execution_auth")
_emit_validates_capability("p2", "test_telemetry_emitter", "capability_check")
_emit_routes_to_capability("p2", "test_telemetry_emitter", "capability_route")
_emit_writes_via_uwg("p2", "test_telemetry_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "test_telemetry_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "test_telemetry_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "test_telemetry_emitter", "exec_output")
_emit_dispatches_agent("p3", "test_telemetry_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "test_telemetry_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_telemetry_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_telemetry_emitter", "healing_outcome")
_emit_escalates_failure("p3", "test_telemetry_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_telemetry_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_telemetry_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_telemetry_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_telemetry_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_telemetry_emitter", "eval_metric")
_emit_stores_embedding("p4", "test_telemetry_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_telemetry_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_telemetry_emitter", "exec_snapshot_link")


@pytest.mark.unit
class TestComputeEventHash:
    """Test compute_event_hash deterministic hash calculation."""

    def test_deterministic_hash_same_inputs(self):
        """Test same inputs produce identical hash."""
        details = {"key1": "value1", "key2": "value2"}

        hash1 = compute_event_hash("stage1", "kind1", 123, details)
        hash2 = compute_event_hash("stage1", "kind1", 123, details)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_different_inputs_produce_different_hashes(self):
        """Test different inputs produce different hashes."""
        details = {"key": "value"}

        hash1 = compute_event_hash("stage1", "kind1", 123, details)
        hash2 = compute_event_hash("stage2", "kind1", 123, details)  # Different stage

        assert hash1 != hash2

    def test_details_key_order_does_not_affect_hash(self):
        """Test details key order does not affect event hash."""
        details1 = {"z": "last", "a": "first", "m": "middle"}
        details2 = {"a": "first", "m": "middle", "z": "last"}

        hash1 = compute_event_hash("stage", "kind", 42, details1)
        hash2 = compute_event_hash("stage", "kind", 42, details2)

        assert hash1 == hash2


@pytest.mark.unit
class TestTelemetryEvent:
    """Test TelemetryEvent immutable dataclass."""

    def test_create_with_deterministic_event_hash(self):
        """Test event creation with deterministic hash."""
        details = {"metric": "cpu_usage", "value": 85.5}

        event = TelemetryEvent.create(
            trace_id="trace123", stage="processing", kind="metric", commit_tick=42, details=details
        )

        assert event.trace_id == "trace123"
        assert event.stage == "processing"
        assert event.kind == "metric"
        assert event.commit_tick == 42
        assert event.details == details
        assert event.event_hash is not None
        assert len(event.event_hash) == 64

    def test_determinism_same_inputs_same_hash(self):
        """Test determinism: same inputs => same event_hash."""
        details = {"action": "process", "items": 10}

        event1 = TelemetryEvent.create(
            trace_id="trace123", stage="stage1", kind="action", commit_tick=100, details=details
        )

        event2 = TelemetryEvent.create(
            trace_id="trace123", stage="stage1", kind="action", commit_tick=100, details=details
        )

        assert event1.event_hash == event2.event_hash

    def test_details_key_order_does_not_affect_event_hash(self):
        """Test details key order does not affect event hash."""
        details1 = {"z": "last", "a": "first"}
        details2 = {"a": "first", "z": "last"}

        event1 = TelemetryEvent.create(
            trace_id="trace456", stage="test", kind="order_test", commit_tick=1, details=details1
        )

        event2 = TelemetryEvent.create(
            trace_id="trace456", stage="test", kind="order_test", commit_tick=1, details=details2
        )

        assert event1.event_hash == event2.event_hash

    def test_no_mutation_details_deep_copied(self):
        """Test modifying original details dict after construction does not change stored details."""
        original_details = {"counter": 0, "status": "initial"}

        event = TelemetryEvent.create(
            trace_id="trace789", stage="mutation_test", kind="test", commit_tick=999, details=original_details
        )

        # Modify original details after event creation
        original_details["counter"] = 999
        original_details["status"] = "modified"
        original_details["new_field"] = "added"

        # Event details should remain unchanged
        assert event.details["counter"] == 0
        assert event.details["status"] == "initial"
        assert "new_field" not in event.details

    def test_event_immutability(self):
        """Test event is immutable."""
        details = {"test": "value"}
        event = TelemetryEvent.create(
            trace_id="trace", stage="stage", kind="kind", commit_tick=1, details=details
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            event.trace_id = "changed"

        with pytest.raises(AttributeError):
            event.stage = "changed"

        with pytest.raises(AttributeError):
            event.kind = "changed"

        with pytest.raises(AttributeError):
            event.commit_tick = 999

        with pytest.raises(AttributeError):
            event.details = {"changed": "value"}

        with pytest.raises(AttributeError):
            event.event_hash = "changed"


@pytest.mark.unit
class TestTelemetryEmitter:
    """Test TelemetryEmitter write-only behavior."""

    def test_emit_calls_injected_record_fn_exactly_once(self):
        """Test emit calls injected record_fn exactly once with same object."""
        emitter = TelemetryEmitter()

        details = {"metric": "test", "value": 42}
        event = TelemetryEvent.create(
            trace_id="trace123", stage="test_stage", kind="test_kind", commit_tick=1, details=details
        )

        # Track calls to record_fn
        calls = []

        def mock_record_fn(telemetry_event):
            calls.append(telemetry_event)

        emitter.emit(event=event, record_fn=mock_record_fn)

        # Should call record_fn exactly once
        assert len(calls) == 1
        assert calls[0] is event  # Same object reference

    def test_emit_performs_no_mutation(self):
        """Test emit performs no mutation of event."""
        emitter = TelemetryEmitter()

        details = {"original": "value"}
        event = TelemetryEvent.create(
            trace_id="trace456", stage="mutation_test", kind="test", commit_tick=123, details=details
        )

        # Snapshot original event
        original_hash = event.event_hash
        original_details = event.details.copy()

        def mock_record_fn(telemetry_event):
            # Verify event unchanged during emit
            assert telemetry_event.event_hash == original_hash
            assert telemetry_event.details == original_details

        emitter.emit(event=event, record_fn=mock_record_fn)

        # Verify event unchanged after emit
        assert event.event_hash == original_hash
        assert event.details == original_details

    def test_emit_no_branching_logic(self):
        """Test emit has no branching logic - always calls record_fn."""
        emitter = TelemetryEmitter()

        # Test with different event types
        events = [
            TelemetryEvent.create("trace1", "stage1", "kind1", 1, {"a": 1}),
            TelemetryEvent.create("trace2", "stage2", "kind2", 2, {"b": 2}),
            TelemetryEvent.create("trace3", "stage3", "kind3", 3, {"c": 3}),
        ]

        for event in events:
            calls = []

            def mock_record_fn(telemetry_event):
                calls.append(telemetry_event)

            emitter.emit(event=event, record_fn=mock_record_fn)

            # Should always call record_fn exactly once
            assert len(calls) == 1
            assert calls[0] is event

    def test_build_event_convenience_constructor(self):
        """Test build_event convenience constructor."""
        emitter = TelemetryEmitter()

        details = {"convenience": "test"}
        event = emitter.build_event(
            trace_id="trace789",
            stage="convenience_stage",
            kind="convenience_kind",
            commit_tick=456,
            details=details,
        )

        # Verify event properties
        assert event.trace_id == "trace789"
        assert event.stage == "convenience_stage"
        assert event.kind == "convenience_kind"
        assert event.commit_tick == 456
        assert event.details == details
        assert event.event_hash is not None
        assert len(event.event_hash) == 64

        # Verify it's a proper TelemetryEvent
        assert isinstance(event, TelemetryEvent)

    def test_build_event_equivalent_to_direct_create(self):
        """Test build_event produces same result as direct TelemetryEvent.create."""
        emitter = TelemetryEmitter()

        details = {"equivalence": "test"}

        # Create event using build_event
        event1 = emitter.build_event(
            trace_id="trace999", stage="equivalence", kind="test", commit_tick=789, details=details
        )

        # Create event using direct create
        event2 = TelemetryEvent.create(
            trace_id="trace999", stage="equivalence", kind="test", commit_tick=789, details=details
        )

        # Should be identical
        assert event1.trace_id == event2.trace_id
        assert event1.stage == event2.stage
        assert event1.kind == event2.kind
        assert event1.commit_tick == event2.commit_tick
        assert event1.details == event2.details
        assert event1.event_hash == event2.event_hash
