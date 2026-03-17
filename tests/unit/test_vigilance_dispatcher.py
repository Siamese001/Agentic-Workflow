"""
Unit tests for L6 Observability Vigilance Dispatcher - pure event dispatch.
"""

import pytest

from agentic_core.L6_observability.engines.vigilance_dispatcher import (
    VigilanceDispatcher,
    VigilanceEventArtifact,
    to_meta_payload,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_routes_to_agent,
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
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_agent_executes_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_1")
_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_2")
_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_3")
_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_4")
_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_5")
_emit_emits_metric_event("test_vigilance_dispatcher", "p4obs", "metric_6")
_emit_records_incident_event("test_vigilance_dispatcher", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_vigilance_dispatcher", "p4obs", "anomaly")
_emit_writes_observability_log("test_vigilance_dispatcher", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_vigilance_dispatcher", "p4obs", "mon_state")
_emit_triggers_alert("test_vigilance_dispatcher", "p4obs", "alert")
_emit_links_incident_trace("test_vigilance_dispatcher", "p4obs", "trace_link")
_emit_captures_pattern("test_vigilance_dispatcher", "p3lm", "pattern")
_emit_records_learning_event("test_vigilance_dispatcher", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_vigilance_dispatcher", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_vigilance_dispatcher", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_vigilance_dispatcher", "p3lm", "routing")
_emit_improves_agent_policy("test_vigilance_dispatcher", "p3lm", "policy")
_emit_stores_learning_state("test_vigilance_dispatcher", "p3lm", "state")
_emit_records_execution_trace("test_vigilance_dispatcher", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_vigilance_dispatcher", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_vigilance_dispatcher", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_vigilance_dispatcher", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_vigilance_dispatcher", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_vigilance_dispatcher", "env_read", "p2_env_1")
_emit_reads_environ("test_vigilance_dispatcher", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_vigilance_dispatcher", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_vigilance_dispatcher", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_vigilance_dispatcher")
_emit_applies_guardrail("p0", "test_vigilance_dispatcher", "p0_governance")
_emit_reads_policy_state("p0", "test_vigilance_dispatcher", "policy_binding")
_emit_routes_to_agent("p1", "test_vigilance_dispatcher", "test")
_emit_orchestrates_workflow("p1", "test_vigilance_dispatcher", "test")
_emit_dispatches_execution_plan("p1", "test_vigilance_dispatcher", "test")
_emit_validates_agent_capability("p1", "test_vigilance_dispatcher", "test")
_emit_checks_agent_registry("p1", "test_vigilance_dispatcher", "test")
_emit_snapshots_state("p0", "test_vigilance_dispatcher", "state_snapshot")
_emit_pulls_context("p1", "test_vigilance_dispatcher", "context_pull")
_emit_pulls_context("p1", "test_vigilance_dispatcher", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_vigilance_dispatcher", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_vigilance_dispatcher", "uwg_term_secondary")
_emit_writes_through("p1", "test_vigilance_dispatcher", "write_through")
_emit_writes_through("p1", "test_vigilance_dispatcher", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_vigilance_dispatcher", "safety_validation")
_emit_invokes_eval("p1", "test_vigilance_dispatcher", "eval_call")
_emit_proposal_commits_routing("p1", "test_vigilance_dispatcher", "routing_commit")
_emit_escalates_to_human("p1", "test_vigilance_dispatcher", "human_escalation")
_emit_routes_through("p1", "test_vigilance_dispatcher", "route_through")
_emit_agent_executes_agent("p1", "test_vigilance_dispatcher", "sub_agent")
_emit_verifies_policy("p1", "test_vigilance_dispatcher", "policy_check")
_emit_observes_runtime_state("p1", "test_vigilance_dispatcher", "runtime_state")
_emit_verifies_boundary("p1", "test_vigilance_dispatcher", "boundary_check")
_emit_transcripts_response("p1", "test_vigilance_dispatcher", "transcript")
_emit_hard_fails_untranscripted("p1", "test_vigilance_dispatcher")
_emit_gated_by_confidence("p1", "test_vigilance_dispatcher", "confidence_gate")
emit_replay_key("p0", "test_vigilance_dispatcher")
emit_determinism_digest("p0", "test_vigilance_dispatcher")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vigilance_dispatcher", "execution_auth")
_emit_validates_capability("p2", "test_vigilance_dispatcher", "capability_check")
_emit_routes_to_capability("p2", "test_vigilance_dispatcher", "capability_route")
_emit_writes_via_uwg("p2", "test_vigilance_dispatcher", "uwg_write")
_emit_blocks_direct_write("p2", "test_vigilance_dispatcher", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vigilance_dispatcher", "tool_invocation")
_emit_captures_execution_output("p2", "test_vigilance_dispatcher", "exec_output")
_emit_dispatches_agent("p3", "test_vigilance_dispatcher", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vigilance_dispatcher", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vigilance_dispatcher", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vigilance_dispatcher", "healing_outcome")
_emit_escalates_failure("p3", "test_vigilance_dispatcher", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vigilance_dispatcher", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vigilance_dispatcher", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vigilance_dispatcher", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vigilance_dispatcher", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vigilance_dispatcher", "eval_metric")
_emit_stores_embedding("p4", "test_vigilance_dispatcher", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vigilance_dispatcher", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vigilance_dispatcher", "exec_snapshot_link")


@pytest.mark.unit
class TestVigilanceEventArtifact:
    """Test VigilanceEventArtifact dataclass and signal normalization."""

    def test_create_with_normalized_signals(self):
        """Test create normalizes signals to sorted unique."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123",
            signals=("signal3", "signal1", "signal2", "signal1"),  # duplicate and unsorted
            summary="Test event",
        )

        assert artifact.trace_id == "trace123"
        assert artifact.signals == ("signal1", "signal2", "signal3")  # sorted unique
        assert artifact.summary == "Test event"

    def test_signals_empty_tuple(self):
        """Test empty signals tuple remains empty."""
        artifact = VigilanceEventArtifact.create(trace_id="trace123", signals=(), summary="Empty signals")

        assert artifact.signals == ()

    def test_signals_single_element(self):
        """Test single signal remains unchanged."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1",), summary="Single signal"
        )

        assert artifact.signals == ("signal1",)

    def test_signals_already_sorted_unique(self):
        """Test already sorted unique signals remain unchanged."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Already sorted"
        )

        assert artifact.signals == ("signal1", "signal2", "signal3")

    def test_signals_with_duplicates(self):
        """Test duplicate signals are removed."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123",
            signals=("signal1", "signal2", "signal1", "signal3", "signal2"),
            summary="With duplicates",
        )

        assert artifact.signals == ("signal1", "signal2", "signal3")

    def test_artifact_immutability(self):
        """Test artifact is immutable."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Test"
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            artifact.trace_id = "changed"

        with pytest.raises(AttributeError):
            artifact.signals = ("changed",)

        with pytest.raises(AttributeError):
            artifact.summary = "changed"


@pytest.mark.unit
class TestVigilanceDispatcher:
    """Test VigilanceDispatcher pure dispatch behavior."""

    def test_dispatch_calls_enqueue_fn_once(self):
        """Test dispatch calls enqueue_fn exactly once with same object."""
        dispatcher = VigilanceDispatcher()
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Test event"
        )

        # Track calls to enqueue_fn
        calls = []

        def mock_enqueue_fn(artifact):
            calls.append(artifact)

        dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

        assert len(calls) == 1
        assert calls[0] is event  # Same object reference

    def test_dispatch_no_branching_logic(self):
        """Test dispatch has no branching logic - always calls enqueue."""
        dispatcher = VigilanceDispatcher()

        # Test with different event types
        events = [
            VigilanceEventArtifact.create("trace1", (), "empty"),
            VigilanceEventArtifact.create("trace2", ("signal1",), "single"),
            VigilanceEventArtifact.create("trace3", ("signal1", "signal2"), "multiple"),
        ]

        for event in events:
            calls = []

            def mock_enqueue_fn(artifact):
                calls.append(artifact)

            dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

            # Should always call enqueue exactly once
            assert len(calls) == 1
            assert calls[0] is event

    def test_dispatch_no_state_mutation(self):
        """Test dispatch does not mutate state or event."""
        dispatcher = VigilanceDispatcher()
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Original"
        )

        # Snapshot original state
        original_trace = event.trace_id
        original_signals = event.signals
        original_summary = event.summary

        def mock_enqueue_fn(artifact):
            # Verify event hasn't changed during dispatch
            assert artifact.trace_id == original_trace
            assert artifact.signals == original_signals
            assert artifact.summary == original_summary

        dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

        # Verify event unchanged after dispatch
        assert event.trace_id == original_trace
        assert event.signals == original_signals
        assert event.summary == original_summary


@pytest.mark.unit
class TestToMetaPayload:
    """Test to_meta_payload conversion function."""

    def test_adapter_output_stable_and_deterministic(self):
        """Test adapter output is stable and deterministic."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Test event"
        )

        payload1 = to_meta_payload(event)
        payload2 = to_meta_payload(event)

        assert payload1 == payload2
        assert payload1 == {
            "trace_id": "trace123",
            "signals": ["signal1", "signal2", "signal3"],
            "summary": "Test event",
        }

    def test_adapter_no_mutation_of_event(self):
        """Test adapter does not mutate the event."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Original"
        )

        original_event = event

        payload = to_meta_payload(event)

        # Event should be unchanged
        assert event is original_event
        assert event.trace_id == "trace123"
        assert event.signals == ("signal1", "signal2")
        assert event.summary == "Original"

        # Payload should have converted tuple to list
        assert payload["signals"] == ["signal1", "signal2"]
        assert isinstance(payload["signals"], list)

    def test_adapter_with_empty_signals(self):
        """Test adapter with empty signals."""
        event = VigilanceEventArtifact.create(trace_id="trace123", signals=(), summary="Empty signals")

        payload = to_meta_payload(event)

        assert payload == {"trace_id": "trace123", "signals": [], "summary": "Empty signals"}

    def test_adapter_signals_order_matches_event(self):
        """Test signals list order matches event.signals (already sorted)."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Ordered signals"
        )

        payload = to_meta_payload(event)

        # Order should match event.signals
        assert payload["signals"] == ["signal1", "signal2", "signal3"]
        assert list(event.signals) == payload["signals"]
