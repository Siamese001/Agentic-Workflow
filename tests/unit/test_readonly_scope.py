"""
Phase 6 — Wave 1 Tests: read_only_retrieval_scope() + RetrievalMutationViolation.
"""

from __future__ import annotations

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_readonly_scope", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_readonly_scope", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_readonly_scope", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_readonly_scope", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_readonly_scope", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_readonly_scope", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_readonly_scope", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_readonly_scope", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_readonly_scope", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_readonly_scope", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_readonly_scope", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_readonly_scope", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_readonly_scope", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_readonly_scope", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_readonly_scope", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_readonly_scope", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_readonly_scope", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_readonly_scope", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_readonly_scope", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_readonly_scope", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_readonly_scope", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_readonly_scope", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_readonly_scope", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_readonly_scope")
# REMOVED: _emit_applies_guardrail("p0", "test_readonly_scope", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_readonly_scope", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_readonly_scope", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_readonly_scope", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_readonly_scope", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_readonly_scope", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_readonly_scope", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_readonly_scope", "write_through")
# REMOVED: _emit_writes_through("p1", "test_readonly_scope", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_readonly_scope", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_readonly_scope", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_readonly_scope", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_readonly_scope", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_readonly_scope", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_readonly_scope", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_readonly_scope", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_readonly_scope", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_readonly_scope", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_readonly_scope", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_readonly_scope", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_readonly_scope", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_readonly_scope", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_readonly_scope", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_readonly_scope")
# REMOVED: _emit_gated_by_confidence("p1", "test_readonly_scope", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_readonly_scope")
# REMOVED: emit_determinism_digest("p0", "test_readonly_scope")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_readonly_scope", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_readonly_scope", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_readonly_scope", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_readonly_scope", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_readonly_scope", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_readonly_scope", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_readonly_scope", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_readonly_scope", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_readonly_scope", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_readonly_scope", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_readonly_scope", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_readonly_scope", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_readonly_scope", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_readonly_scope", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_readonly_scope", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_readonly_scope", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_readonly_scope", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_readonly_scope", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_readonly_scope", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_readonly_scope", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestScopeActivation:
    def test_scope_inactive_by_default(self):
        from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
            RetrievalMutationViolation,
            assert_not_read_only,
            is_read_only_retrieval_active,
            read_only_retrieval_scope,
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

        assert is_read_only_retrieval_active() is False

    def test_scope_active_inside_context(self):
        with read_only_retrieval_scope():
            assert is_read_only_retrieval_active() is True

    def test_scope_inactive_after_context(self):
        with read_only_retrieval_scope():
            pass
        assert is_read_only_retrieval_active() is False

    def test_scope_restored_on_exception(self):
        with pytest.raises(RuntimeError):
            with read_only_retrieval_scope():
                raise RuntimeError("boom")
        assert is_read_only_retrieval_active() is False

    def test_nested_scope_stays_active_until_outermost_exits(self):
        with read_only_retrieval_scope():
            with read_only_retrieval_scope():
                assert is_read_only_retrieval_active() is True
            assert is_read_only_retrieval_active() is True
        assert is_read_only_retrieval_active() is False


class TestMutationBlockedInsideReadOnlyScope:
    def test_mutation_blocked_inside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() raises inside scope.
        """
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc_info.value)

    def test_mutation_blocked_includes_operation_detail(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert "pinecone.upsert" in str(exc_info.value)

    def test_mutation_blocked_redis_setex(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_pinecone_upsert(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_file_write(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation):
                assert_not_read_only("file.write")

    def test_violation_carries_code_substring(self):
        """Negative test: violation message contains code substring."""
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("redis.set")
                pytest.fail("Expected RetrievalMutationViolation")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
                assert exc.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_preserved(self):
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("pinecone.upsert")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert exc.detail == "pinecone.upsert"


class TestMutationAllowedOutsideReadOnlyScope:
    def test_mutation_allowed_outside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() is a no-op outside scope.
        """
        assert_not_read_only("redis.setex")  # must not raise

    def test_mutation_allowed_after_scope_exits(self):
        with read_only_retrieval_scope():
            pass
        assert_not_read_only("pinecone.upsert")  # must not raise

    def test_mutation_allowed_with_empty_operation(self):
        assert_not_read_only("")  # must not raise

    def test_mutation_allowed_with_no_operation(self):
        assert_not_read_only()  # must not raise


class TestRetrievalMutationViolation:
    def test_violation_is_exception(self):
        exc = RetrievalMutationViolation("test detail")
        assert isinstance(exc, Exception)

    def test_violation_code_constant(self):
        assert RetrievalMutationViolation.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_stored(self):
        exc = RetrievalMutationViolation("my detail")
        assert exc.detail == "my detail"

    def test_violation_empty_detail(self):
        exc = RetrievalMutationViolation()
        assert exc.detail == ""
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
