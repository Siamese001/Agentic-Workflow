"""Unit tests for system_learning.validators.replay_validator."""

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

# REMOVED: _emit_authorize_and_execute("p2", "test_replay_validator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_replay_validator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_replay_validator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_replay_validator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_replay_validator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_replay_validator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_replay_validator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_replay_validator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_replay_validator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_replay_validator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_replay_validator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_replay_validator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_replay_validator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_replay_validator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_replay_validator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_replay_validator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_replay_validator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_replay_validator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_replay_validator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_replay_validator", "exec_snapshot_link")
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
#  # MOVED: from system_learning.validators.replay_validator import (
    DeterminismViolation,
    replay_validate,
)

# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_replay_validator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_replay_validator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_replay_validator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_replay_validator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_replay_validator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_replay_validator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_replay_validator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_replay_validator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_replay_validator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_replay_validator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_replay_validator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_replay_validator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_replay_validator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_replay_validator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_replay_validator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_replay_validator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_replay_validator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_replay_validator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_replay_validator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_replay_validator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_replay_validator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_replay_validator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_replay_validator", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_replay_validator")
# REMOVED: _emit_applies_guardrail("p0", "test_replay_validator", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_replay_validator", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_replay_validator", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_replay_validator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_replay_validator", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_validator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_validator", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_replay_validator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_replay_validator", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_replay_validator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_replay_validator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_replay_validator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_replay_validator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_replay_validator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_replay_validator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_replay_validator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_replay_validator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_replay_validator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_replay_validator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_replay_validator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_replay_validator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_replay_validator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_replay_validator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_replay_validator")
# REMOVED: _emit_gated_by_confidence("p1", "test_replay_validator", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_replay_validator")
# REMOVED: emit_determinism_digest("p0", "test_replay_validator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestReplayValidator:
    def test_deterministic_engine_passes(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.validators.replay_validator import (
        """Deterministic engine produces same hash on both runs."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}
        hash_result = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        # Should return a valid SHA-256 hex digest
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_nondeterministic_engine_fails(self):
        """Non-deterministic engine raises DeterminismViolation."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": snapshot["input"] * call_count}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation, match="DETERMINISM_VIOLATION"):
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

    def test_error_includes_both_hashes(self):
        """DeterminismViolation error includes both hashes."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": call_count}

        def canonicalize(output):
            return str(output).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation) as exc_info:
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

        error_msg = str(exc_info.value)
        assert "Run 1 hash:" in error_msg
        assert "Run 2 hash:" in error_msg

    def test_same_output_twice_produces_same_hash(self):
        """Running replay_validate twice with same engine produces same hash."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2

    def test_different_snapshots_produce_different_hashes(self):
        """Different snapshots produce different hashes."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot1 = {"input": 5}
        snapshot2 = {"input": 10}

        hash1 = replay_validate(snapshot1, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot2, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 != hash2


class TestDeterminism:
    def test_replay_validate_deterministic(self):
    """Test replay_validate_deterministic contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
        hash3 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2 == hash3
