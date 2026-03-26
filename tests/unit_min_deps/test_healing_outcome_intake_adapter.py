"""Tests for HealingOutcomeIntakeAdapter."""

import pytest

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

# REMOVED: _emit_authorize_and_execute("p2", "test_healing_outcome_intake_adapter", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_outcome_intake_adapter", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_outcome_intake_adapter", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_outcome_intake_adapter", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_outcome_intake_adapter", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_outcome_intake_adapter", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_outcome_intake_adapter", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_outcome_intake_adapter", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_outcome_intake_adapter", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_outcome_intake_adapter", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_outcome_intake_adapter", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_outcome_intake_adapter", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_outcome_intake_adapter", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_outcome_intake_adapter", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_outcome_intake_adapter", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_outcome_intake_adapter", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_outcome_intake_adapter", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_outcome_intake_adapter", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_outcome_intake_adapter", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_outcome_intake_adapter", "exec_snapshot_link")
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
#  # MOVED: from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
#  # MOVED: from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
#  # MOVED: from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
#  # MOVED: from system_learning.types.healing_outcome_types import HealingOutcomeEvent

# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_intake_adapter", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_outcome_intake_adapter", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_outcome_intake_adapter", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_outcome_intake_adapter", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_outcome_intake_adapter", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_outcome_intake_adapter", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_outcome_intake_adapter", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_outcome_intake_adapter", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_outcome_intake_adapter", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_outcome_intake_adapter", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_outcome_intake_adapter", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_outcome_intake_adapter", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_outcome_intake_adapter", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_outcome_intake_adapter", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_intake_adapter", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_intake_adapter", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_intake_adapter", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_intake_adapter", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_intake_adapter", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_outcome_intake_adapter", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_outcome_intake_adapter", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_outcome_intake_adapter", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_outcome_intake_adapter", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_outcome_intake_adapter")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_outcome_intake_adapter", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_outcome_intake_adapter", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_outcome_intake_adapter", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_healing_outcome_intake_adapter", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_outcome_intake_adapter", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_outcome_intake_adapter", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_outcome_intake_adapter", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_healing_outcome_intake_adapter", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_outcome_intake_adapter", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_outcome_intake_adapter", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_outcome_intake_adapter", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_outcome_intake_adapter", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_outcome_intake_adapter", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_outcome_intake_adapter", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_outcome_intake_adapter", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_outcome_intake_adapter", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_outcome_intake_adapter", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_outcome_intake_adapter", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_outcome_intake_adapter", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_outcome_intake_adapter", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_outcome_intake_adapter", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_outcome_intake_adapter", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_outcome_intake_adapter", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_outcome_intake_adapter")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_outcome_intake_adapter", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_outcome_intake_adapter")
# REMOVED: emit_determinism_digest("p0", "test_healing_outcome_intake_adapter")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit_min_deps
class TestHealingOutcomeIntakeAdapter:
    """Test suite for HealingOutcomeIntakeAdapter."""

    def test_build_record_determinism(self) -> None:
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
                from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
                from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
                from system_learning.types.healing_outcome_types import HealingOutcomeEvent
                """Test that identical inputs produce identical records."""
                # Setup
                store = InMemoryHealingOutcomeIntakeStore()
                adapter = HealingOutcomeIntakeAdapter(store)

        adapter = HealingOutcomeIntakeAdapter(store)

        # Create two aggregators with identical events
        event1 = HealingOutcomeEvent(
            healer_id="healer1", tier="LOCAL_AGENT", failure_type="timeout", success=False, timestamp_utc=1000
        )
        event2 = HealingOutcomeEvent(
            healer_id="healer2", tier="QWEN_VLLM", failure_type="exception", success=True, timestamp_utc=2000
        )

        # Build first record
        aggregator1 = HealingOutcomeAggregator(window_size=10)
        aggregator1.ingest(event1)
        aggregator1.ingest(event2)
        record1 = adapter.build_record(aggregator1, created_utc=3000, source="test")

        # Build second record with same inputs
        aggregator2 = HealingOutcomeAggregator(window_size=10)
        aggregator2.ingest(event1)
        aggregator2.ingest(event2)
        record2 = adapter.build_record(aggregator2, created_utc=3000, source="test")

        # Assert records are identical
        assert record1 == record2
        assert record1.schema_version == 1
        assert record1.created_utc == 3000
        assert record1.window_size == 2
        assert record1.source == "test"

        # Verify snapshot is sorted deterministically
        snapshot = record1.snapshot
        assert len(snapshot) == 2
        # Should be sorted by (healer_id, tier, failure_type)
        assert snapshot[0].healer_id == "healer1"
        assert snapshot[1].healer_id == "healer2"

    def test_persist_record_calls_store_exactly_once(self) -> None:
    """Test persist_record_calls_store_exactly_once runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute persist_record_calls_store_exactly_once
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        # Persist record
        adapter.persist_record(record)

        # Verify store was called exactly once
        assert store.count() == 1
        stored_records = store.get_records()
        assert len(stored_records) == 1
        assert stored_records[0] == record

    def test_empty_aggregator_raises_error(self) -> None:
        """Test that building record from empty aggregator raises error."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        empty_aggregator = HealingOutcomeAggregator(window_size=10)

        # Should raise ValueError for empty snapshot (window_size validation happens first)
        with pytest.raises(ValueError, match="window_size must be positive"):
            adapter.build_record(empty_aggregator, created_utc=1000, source="test")

    def test_snapshot_sorting_enforced(self) -> None:
        """Test that snapshot is always sorted deterministically."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        # Create events in non-sorted order
        events = [
            HealingOutcomeEvent(
                healer_id="zebra", tier="GEMINI_2_5_PRO", failure_type="z", success=False, timestamp_utc=3000
            ),
            HealingOutcomeEvent(
                healer_id="alpha", tier="LOCAL_AGENT", failure_type="a", success=True, timestamp_utc=1000
            ),
            HealingOutcomeEvent(
                healer_id="beta", tier="QWEN_VLLM", failure_type="b", success=False, timestamp_utc=2000
            ),
        ]

        # Ingest in non-sorted order
        aggregator = HealingOutcomeAggregator(window_size=10)
        for event in events:
            aggregator.ingest(event)

        # Build record
        record = adapter.build_record(aggregator, created_utc=4000, source="test")

        # Verify snapshot is sorted by (healer_id, tier, failure_type)
        snapshot = record.snapshot
        assert len(snapshot) == 3

        # Check sorting order
        assert snapshot[0].healer_id == "alpha"
        assert snapshot[1].healer_id == "beta"
        assert snapshot[2].healer_id == "zebra"

        # Verify tuple is immutable
        with pytest.raises(AttributeError):
            snapshot[0].healer_id = "changed"
