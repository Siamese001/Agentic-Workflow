"""
Unit tests for L2 CID Registry - immutable execution cycle tracking.
"""

import pytest

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_1")
_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_2")
_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_3")
_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_4")
_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_5")
_emit_emits_metric_event("test_cid_registry", "p4obs", "metric_6")
_emit_records_incident_event("test_cid_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_cid_registry", "p4obs", "anomaly")
_emit_writes_observability_log("test_cid_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_cid_registry", "p4obs", "mon_state")
_emit_triggers_alert("test_cid_registry", "p4obs", "alert")
_emit_links_incident_trace("test_cid_registry", "p4obs", "trace_link")
_emit_captures_pattern("test_cid_registry", "p3lm", "pattern")
_emit_records_learning_event("test_cid_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_cid_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_cid_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_cid_registry", "p3lm", "routing")
_emit_improves_agent_policy("test_cid_registry", "p3lm", "policy")
_emit_stores_learning_state("test_cid_registry", "p3lm", "state")
_emit_records_execution_trace("test_cid_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_cid_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_cid_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_cid_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_cid_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_cid_registry", "env_read", "p2_env_1")
_emit_reads_environ("test_cid_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_cid_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_cid_registry", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_cid_registry")
_emit_applies_guardrail("p0", "test_cid_registry", "p0_governance")
_emit_reads_policy_state("p0", "test_cid_registry", "policy_binding")
_emit_snapshots_state("p0", "test_cid_registry", "state_snapshot")
_emit_pulls_context("p1", "test_cid_registry", "context_pull")
_emit_pulls_context("p1", "test_cid_registry", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_cid_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_cid_registry", "uwg_term_secondary")
_emit_writes_through("p1", "test_cid_registry", "write_through")
_emit_writes_through("p1", "test_cid_registry", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_cid_registry", "safety_validation")
_emit_invokes_eval("p1", "test_cid_registry", "eval_call")
_emit_proposal_commits_routing("p1", "test_cid_registry", "routing_commit")
_emit_escalates_to_human("p1", "test_cid_registry", "human_escalation")
_emit_routes_through("p1", "test_cid_registry", "route_through")
_emit_checks_agent_registry("p1", "test_cid_registry", "agent_registry")
_emit_validates_agent_capability("p1", "test_cid_registry", "capability")
_emit_dispatches_execution_plan("p1", "test_cid_registry", "exec_plan")
_emit_agent_executes_agent("p1", "test_cid_registry", "sub_agent")
_emit_routes_to_agent("p1", "test_cid_registry", "target_agent")
_emit_verifies_policy("p1", "test_cid_registry", "policy_check")
_emit_observes_runtime_state("p1", "test_cid_registry", "runtime_state")
_emit_verifies_boundary("p1", "test_cid_registry", "boundary_check")
_emit_transcripts_response("p1", "test_cid_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "test_cid_registry")
_emit_gated_by_confidence("p1", "test_cid_registry", "confidence_gate")
emit_replay_key("p0", "test_cid_registry")
emit_determinism_digest("p0", "test_cid_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_cid_registry", "execution_auth")
_emit_validates_capability("p2", "test_cid_registry", "capability_check")
_emit_routes_to_capability("p2", "test_cid_registry", "capability_route")
_emit_writes_via_uwg("p2", "test_cid_registry", "uwg_write")
_emit_blocks_direct_write("p2", "test_cid_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "test_cid_registry", "tool_invocation")
_emit_captures_execution_output("p2", "test_cid_registry", "exec_output")
_emit_dispatches_agent("p3", "test_cid_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "test_cid_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_cid_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_cid_registry", "healing_outcome")
_emit_escalates_failure("p3", "test_cid_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_cid_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_cid_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_cid_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_cid_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_cid_registry", "eval_metric")
_emit_stores_embedding("p4", "test_cid_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_cid_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_cid_registry", "exec_snapshot_link")


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
class TestExecutionCycle:
    """Test ExecutionCycle dataclass properties."""

    def test_execution_cycle_creation(self):
        """Test ExecutionCycle creation and properties."""
        cycle = ExecutionCycle(cid="test123", attempt=1, status="new")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"
        assert cycle == ExecutionCycle(cid="test123", attempt=1, status="new")

    def test_execution_cycle_immutability(self):
        """Test ExecutionCycle is immutable."""
        cycle = ExecutionCycle(cid="test123", attempt=1, status="new")

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            cycle.attempt = 2

        with pytest.raises(AttributeError):
            cycle.status = "changed"


@pytest.mark.unit
class TestCIDRegistry:
    """Test deterministic CIDRegistry implementation."""

    def test_new_cycle_creates_with_attempt_1(self):
        """Test new_cycle creates cycle with attempt=1 and status='new'."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"

    def test_same_cid_independent_cycles_allowed(self):
        """Test same CID creates independent cycles when called multiple times."""
        registry = CIDRegistry()

        cycle1 = registry.new_cycle("same_cid")
        cycle2 = registry.new_cycle("same_cid")

        # Should create new cycles, not return existing
        assert cycle1.attempt == 1
        assert cycle2.attempt == 1
        assert cycle1.status == "new"
        assert cycle2.status == "new"
        assert cycle1 is not cycle2

    def test_next_attempt_increments_deterministically(self):
        """Test next_attempt increments attempt deterministically."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")
        next_cycle = registry.next_attempt(cycle)

        assert next_cycle.cid == "test123"
        assert next_cycle.attempt == 2
        assert next_cycle.status == "retry"

    def test_next_attempt_multiple_increments(self):
        """Test multiple next_attempt calls increment correctly."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")
        cycle2 = registry.next_attempt(cycle)
        cycle3 = registry.next_attempt(cycle2)
        cycle4 = registry.next_attempt(cycle3)

        assert cycle.attempt == 1
        assert cycle2.attempt == 2
        assert cycle3.attempt == 3
        assert cycle4.attempt == 4

    def test_get_cycle_returns_current_cycle(self):
        """Test get_cycle returns the most recent cycle for CID."""
        registry = CIDRegistry()

        original = registry.new_cycle("test123")
        updated = registry.next_attempt(original)

        retrieved = registry.get_cycle("test123")

        assert retrieved == updated
        assert retrieved.attempt == 2

    def test_get_cycle_nonexistent_returns_none(self):
        """Test get_cycle returns None for non-existent CID."""
        registry = CIDRegistry()

        result = registry.get_cycle("nonexistent")

        assert result is None

    def test_update_status_changes_status_only(self):
        """Test update_status changes only status field."""
        registry = CIDRegistry()

        _ = registry.new_cycle("test123")
        updated = registry.update_status("test123", "completed")

        assert updated is not None
        assert updated.cid == "test123"
        assert updated.attempt == 1  # unchanged
        assert updated.status == "completed"

    def test_update_status_nonexistent_returns_none(self):
        """Test update_status returns None for non-existent CID."""
        registry = CIDRegistry()

        result = registry.update_status("nonexistent", "status")

        assert result is None

    def test_deterministic_behavior_same_inputs(self):
        """Test deterministic behavior with same inputs."""
        registry1 = CIDRegistry()
        registry2 = CIDRegistry()

        # Create same cycles in both registries
        cycle1a = registry1.new_cycle("test")
        cycle1b = registry1.next_attempt(cycle1a)
        cycle1c = registry1.update_status("test", "done")

        cycle2a = registry2.new_cycle("test")
        cycle2b = registry2.next_attempt(cycle2a)
        cycle2c = registry2.update_status("test", "done")

        # Should produce identical results
        assert cycle1a.attempt == cycle2a.attempt
        assert cycle1b.attempt == cycle2b.attempt
        assert cycle1c.status == cycle2c.status

    def test_multiple_cids_independent_tracking(self):
        """Test multiple CIDs tracked independently."""
        registry = CIDRegistry()

        # Create cycles for different CIDs
        cycle_a1 = registry.new_cycle("cid_a")
        registry.new_cycle("cid_b")
        registry.next_attempt(cycle_a1)

        # Verify independent tracking
        assert registry.get_cycle("cid_a").attempt == 2
        assert registry.get_cycle("cid_b").attempt == 1
