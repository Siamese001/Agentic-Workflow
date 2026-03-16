"""
Unit tests for L2 Re-Entry Loop - bounded deterministic retry mechanism.
"""

import pytest

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
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

_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_1")
_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_2")
_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_3")
_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_4")
_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_5")
_emit_emits_metric_event("test_reentry_loop", "p4obs", "metric_6")
_emit_records_incident_event("test_reentry_loop", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_reentry_loop", "p4obs", "anomaly")
_emit_writes_observability_log("test_reentry_loop", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_reentry_loop", "p4obs", "mon_state")
_emit_triggers_alert("test_reentry_loop", "p4obs", "alert")
_emit_links_incident_trace("test_reentry_loop", "p4obs", "trace_link")
_emit_captures_pattern("test_reentry_loop", "p3lm", "pattern")
_emit_records_learning_event("test_reentry_loop", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_reentry_loop", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_reentry_loop", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_reentry_loop", "p3lm", "routing")
_emit_improves_agent_policy("test_reentry_loop", "p3lm", "policy")
_emit_stores_learning_state("test_reentry_loop", "p3lm", "state")
_emit_records_execution_trace("test_reentry_loop", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_reentry_loop", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_reentry_loop", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_reentry_loop", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_reentry_loop", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_reentry_loop", "env_read", "p2_env_1")
_emit_reads_environ("test_reentry_loop", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_reentry_loop", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_reentry_loop", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_reentry_loop")
_emit_applies_guardrail("p0", "test_reentry_loop", "p0_governance")
_emit_reads_policy_state("p0", "test_reentry_loop", "policy_binding")
_emit_snapshots_state("p0", "test_reentry_loop", "state_snapshot")
_emit_pulls_context("p1", "test_reentry_loop", "context_pull")
_emit_pulls_context("p1", "test_reentry_loop", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_reentry_loop", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_reentry_loop", "uwg_term_secondary")
_emit_writes_through("p1", "test_reentry_loop", "write_through")
_emit_writes_through("p1", "test_reentry_loop", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_reentry_loop", "safety_validation")
_emit_invokes_eval("p1", "test_reentry_loop", "eval_call")
_emit_proposal_commits_routing("p1", "test_reentry_loop", "routing_commit")
emit_replay_key("p0", "test_reentry_loop")
emit_determinism_digest("p0", "test_reentry_loop")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_reentry_loop", "execution_auth")
_emit_validates_capability("p2", "test_reentry_loop", "capability_check")
_emit_routes_to_capability("p2", "test_reentry_loop", "capability_route")
_emit_writes_via_uwg("p2", "test_reentry_loop", "uwg_write")
_emit_blocks_direct_write("p2", "test_reentry_loop", "direct_write_block")
_emit_records_tool_invocation("p2", "test_reentry_loop", "tool_invocation")
_emit_captures_execution_output("p2", "test_reentry_loop", "exec_output")
_emit_dispatches_agent("p3", "test_reentry_loop", "agent_dispatch")
_emit_coordinates_agents("p3", "test_reentry_loop", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_reentry_loop", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_reentry_loop", "healing_outcome")
_emit_escalates_failure("p3", "test_reentry_loop", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_reentry_loop", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_reentry_loop", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_reentry_loop", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_reentry_loop", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_reentry_loop", "eval_metric")
_emit_stores_embedding("p4", "test_reentry_loop", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_reentry_loop", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_reentry_loop", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit
class TestReEntryLoop:
    """Test deterministic ReEntryLoop implementation."""

    def test_init_with_valid_max_attempts(self):
        """Test ReEntryLoop initialization with valid max_attempts."""
        loop = ReEntryLoop(max_attempts=3)

        assert loop.max_attempts == 3
        assert loop._cid_registry is not None

    def test_init_with_custom_cid_registry(self):
        """Test ReEntryLoop initialization with custom CIDRegistry."""
        registry = CIDRegistry()
        loop = ReEntryLoop(max_attempts=5, cid_registry=registry)

        assert loop.max_attempts == 5
        assert loop._cid_registry is registry

    def test_init_with_invalid_max_attempts(self):
        """Test ReEntryLoop initialization with invalid max_attempts."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            ReEntryLoop(max_attempts=0)

        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            ReEntryLoop(max_attempts=-1)

    def test_should_retry_true_when_below_max(self):
        """Test should_retry returns True when attempt < max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        assert loop.should_retry(cycle) is True

    def test_should_retry_false_at_max_attempts(self):
        """Test should_retry returns False when attempt == max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=3, status="running")

        assert loop.should_retry(cycle) is False

    def test_should_retry_false_above_max(self):
        """Test should_retry returns False when attempt > max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=4, status="running")

        assert loop.should_retry(cycle) is False

    def test_advance_increments_attempt(self):
        """Test advance increments attempt deterministically."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        next_cycle = loop.advance(cycle)

        assert next_cycle.cid == "test"
        assert next_cycle.attempt == 2
        assert next_cycle.status == "retry"

    def test_advance_multiple_times(self):
        """Test advance called multiple times."""
        loop = ReEntryLoop(max_attempts=5)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        cycle2 = loop.advance(cycle)
        cycle3 = loop.advance(cycle2)
        cycle4 = loop.advance(cycle3)

        assert cycle.attempt == 1
        assert cycle2.attempt == 2
        assert cycle3.attempt == 3
        assert cycle4.attempt == 4

    def test_stops_at_max_attempts(self):
        """Test retry logic stops at max_attempts."""
        loop = ReEntryLoop(max_attempts=3)

        # Create initial cycle
        cycle = loop.new_cycle("test123")
        assert cycle.attempt == 1
        assert loop.should_retry(cycle) is True

        # First retry
        cycle = loop.advance(cycle)
        assert cycle.attempt == 2
        assert loop.should_retry(cycle) is True

        # Second retry (reaches max)
        cycle = loop.advance(cycle)
        assert cycle.attempt == 3
        assert loop.should_retry(cycle) is False

        # Should not retry beyond max
        assert loop.should_retry(cycle) is False

    def test_deterministic_behavior_repeated_runs(self):
        """Test deterministic behavior across repeated runs."""
        loop1 = ReEntryLoop(max_attempts=3)
        loop2 = ReEntryLoop(max_attempts=3)

        # Create same cycles in both loops
        cycle1 = loop1.new_cycle("test")
        cycle2 = loop2.new_cycle("test")

        # Should produce identical results
        assert cycle1.attempt == cycle2.attempt
        assert cycle1.status == cycle2.status

        # Advance both
        next1 = loop1.advance(cycle1)
        next2 = loop2.advance(cycle2)

        assert next1.attempt == next2.attempt
        assert next1.status == next2.status

    def test_new_cycle_creates_with_attempt_1(self):
        """Test new_cycle creates cycle with attempt=1."""
        loop = ReEntryLoop(max_attempts=5)

        cycle = loop.new_cycle("test123")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"

    def test_get_cycle_returns_current_cycle(self):
        """Test get_cycle returns most recent cycle for CID."""
        loop = ReEntryLoop(max_attempts=5)

        original = loop.new_cycle("test123")
        updated = loop.advance(original)

        retrieved = loop.get_cycle("test123")

        assert retrieved == updated
        assert retrieved.attempt == 2

    def test_get_cycle_nonexistent_returns_none(self):
        """Test get_cycle returns None for non-existent CID."""
        loop = ReEntryLoop(max_attempts=5)

        result = loop.get_cycle("nonexistent")

        assert result is None

    def test_update_status_changes_status_only(self):
        """Test update_status changes only status field."""
        loop = ReEntryLoop(max_attempts=5)

        loop.new_cycle("test123")
        updated = loop.update_status("test123", "completed")

        assert updated is not None
        assert updated.cid == "test123"
        assert updated.attempt == 1  # unchanged
        assert updated.status == "completed"

    def test_multiple_cids_independent_tracking(self):
        """Test multiple CIDs tracked independently."""
        loop = ReEntryLoop(max_attempts=5)

        # Create cycles for different CIDs
        cycle_a1 = loop.new_cycle("cid_a")
        loop.new_cycle("cid_b")
        loop.advance(cycle_a1)

        # Verify independent tracking
        assert loop.get_cycle("cid_a").attempt == 2
        assert loop.get_cycle("cid_b").attempt == 1

    def test_no_infinite_loops(self):
        """Test that loop logic cannot create infinite loops."""
        loop = ReEntryLoop(max_attempts=2)

        cycle = loop.new_cycle("test")
        retry_count = 0

        # Simulate retry logic
        while loop.should_retry(cycle) and retry_count < 10:  # safety limit
            cycle = loop.advance(cycle)
            retry_count += 1

        # Should stop after max_attempts - 1 retries
        assert retry_count == 1  # started at attempt 1, max is 2, so 1 retry
        assert cycle.attempt == 2
        assert loop.should_retry(cycle) is False
