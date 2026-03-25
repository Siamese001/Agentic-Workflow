"""Unit tests for BlackboardStore.

Phase 1 Wave 1.2 test suite. Verifies KV operations,
lease semantics, tick monotonicity, and IBlackboardLeaseVerifier compliance.
"""

import pytest

from agentic_core.L4_state.memory.blackboard_store import (
    BlackboardStore,
    LeaseResult,
    SecurityEvent,
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

# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_blackboard_store", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_blackboard_store", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_blackboard_store", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_blackboard_store", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_blackboard_store", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_blackboard_store", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_blackboard_store", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_blackboard_store", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_blackboard_store", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_blackboard_store", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_blackboard_store", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_blackboard_store", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_blackboard_store", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_blackboard_store", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_blackboard_store", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_blackboard_store", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_blackboard_store", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_blackboard_store", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_blackboard_store", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_blackboard_store", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_blackboard_store", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_blackboard_store", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_blackboard_store", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_blackboard_store")
# REMOVED: _emit_applies_guardrail("p0", "test_blackboard_store", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_blackboard_store", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_blackboard_store", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_blackboard_store", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_blackboard_store", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_blackboard_store", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_blackboard_store", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_blackboard_store", "write_through")
# REMOVED: _emit_writes_through("p1", "test_blackboard_store", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_blackboard_store", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_blackboard_store", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_blackboard_store", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_blackboard_store", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_blackboard_store", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_blackboard_store", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_blackboard_store", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_blackboard_store", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_blackboard_store", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_blackboard_store", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_blackboard_store", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_blackboard_store", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_blackboard_store", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_blackboard_store", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_blackboard_store")
# REMOVED: _emit_gated_by_confidence("p1", "test_blackboard_store", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_blackboard_store")
# REMOVED: emit_determinism_digest("p0", "test_blackboard_store")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_blackboard_store", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_blackboard_store", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_blackboard_store", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_blackboard_store", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_blackboard_store", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_blackboard_store", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_blackboard_store", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_blackboard_store", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_blackboard_store", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_blackboard_store", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_blackboard_store", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_blackboard_store", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_blackboard_store", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_blackboard_store", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_blackboard_store", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_blackboard_store", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_blackboard_store", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_blackboard_store", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_blackboard_store", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_blackboard_store", "exec_snapshot_link")


@pytest.mark.unit
class TestBlackboardStore:
    def setup_method(self):
        self.store = BlackboardStore()
        self.store.clear()  # ensure clean state

    def test_set_and_get(self):
        self.store.set("key1", "value1", "agent1", 1)
        assert self.store.get("key1") == "value1"

    def test_get_missing_key_raises(self):
        with pytest.raises(KeyError):
            self.store.get("missing")

    def test_lease_granted_when_no_existing(self):
        result = self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        assert result.success
        assert result.expiry_tick == 15
        assert result.reason == "Lease granted"

    def test_lease_blocks_second_agent(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Agent2 tries same key before expiry
        result = self.store.lease("key1", "agent2", ttl_ticks=5, commit_tick=12)
        assert not result.success
        assert result.expiry_tick == 15
        assert "agent1" in result.reason

    def test_lease_renews_after_expiry(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # After expiry, Agent2 can get lease
        result = self.store.lease("key1", "agent2", ttl_ticks=3, commit_tick=16)
        assert result.success
        assert result.expiry_tick == 19

    def test_lease_same_agent_can_renew_before_expiry(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Same agent can renew
        result = self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=12)
        assert result.success
        assert result.expiry_tick == 17

    def test_lease_ttl_must_be_positive(self):
        result = self.store.lease("key1", "agent1", ttl_ticks=0, commit_tick=10)
        assert not result.success
        assert result.expiry_tick == 0
        assert "positive" in result.reason

    def test_delete_requires_lease(self):
        self.store.set("key1", "value1", "agent1", 1)
        # Try delete without lease
        assert not self.store.delete("key1", "agent1", 1)
        # Get lease then delete
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        assert self.store.delete("key1", "agent1", 10)
        with pytest.raises(KeyError):
            self.store.get("key1")

    def test_delete_wrong_agent_fails(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Wrong agent tries to delete
        assert not self.store.delete("key1", "agent2", 10)

    def test_delete_expired_lease_fails(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Try delete after expiry
        assert not self.store.delete("key1", "agent1", 16)

    def test_verify_healing_lease_interface(self):
        """Test IBlackboardLeaseVerifier.verify_healing_lease implementation."""
        result = self.store.verify_healing_lease("resource", "agent1", 10, "write")
        assert isinstance(result, LeaseResult)
        # Should grant lease with default TTL of 10 ticks
        assert result.success
        assert result.expiry_tick == 20

    def test_log_security_event_interface(self):
        """Test IBlackboardLeaseVerifier.log_security_event implementation."""
        event = SecurityEvent(
            event_type="LEASE_VIOLATION",
            agent_id="agent1",
            resource_path="key1",
            details="Test event",
            timestamp=1234567890,
            severity="medium",
        )
        # Phase 1: no-op, should not raise
        self.store.log_security_event(event)

    def test_multiple_keys_independent(self):
        # Different keys have independent leases
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        self.store.lease("key2", "agent2", ttl_ticks=5, commit_tick=10)
        # Both should succeed
        lease1 = self.store._get_lease("key1")
        lease2 = self.store._get_lease("key2")
        assert lease1.agent_id == "agent1"
        assert lease2.agent_id == "agent2"

    def test_clear_resets_store(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        self.store.clear()
        with pytest.raises(KeyError):
            self.store.get("key1")
        assert self.store._get_lease("key1") is None
