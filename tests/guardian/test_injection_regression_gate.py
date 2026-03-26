"""
Tests for Injection Regression Gate - Guardian Security Tests.

Tests fail-closed regression detection for injection security.
All tests are deterministic and use in-memory fixtures.
"""

import pytest

#  # MOVED: from agentic_core.L5_safety.security.injection_regression_gate import (
    InjectionRegressionError,
    RegressionThresholds,
    check_regression_compliance,
    evaluate_against_baseline,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_injection_regression_gate", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_injection_regression_gate", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_injection_regression_gate", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_injection_regression_gate", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_injection_regression_gate", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_injection_regression_gate", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_injection_regression_gate", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_injection_regression_gate", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_injection_regression_gate", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_injection_regression_gate", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_injection_regression_gate", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_injection_regression_gate", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_injection_regression_gate", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_injection_regression_gate", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_injection_regression_gate", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_injection_regression_gate", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_injection_regression_gate", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_injection_regression_gate", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_injection_regression_gate", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_injection_regression_gate", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_injection_regression_gate", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_injection_regression_gate", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_injection_regression_gate", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_injection_regression_gate")
# REMOVED: _emit_applies_guardrail("p0", "test_injection_regression_gate", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_injection_regression_gate", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_injection_regression_gate", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_injection_regression_gate", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_injection_regression_gate", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_injection_regression_gate", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_injection_regression_gate", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_injection_regression_gate", "write_through")
# REMOVED: _emit_writes_through("p1", "test_injection_regression_gate", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_injection_regression_gate", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_injection_regression_gate", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_injection_regression_gate", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_injection_regression_gate", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_injection_regression_gate", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_injection_regression_gate", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_injection_regression_gate", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_injection_regression_gate", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_injection_regression_gate", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_injection_regression_gate", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_injection_regression_gate", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_injection_regression_gate", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_injection_regression_gate", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_injection_regression_gate", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_injection_regression_gate")
# REMOVED: _emit_gated_by_confidence("p1", "test_injection_regression_gate", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_injection_regression_gate")
# REMOVED: emit_determinism_digest("p0", "test_injection_regression_gate")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_injection_regression_gate", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_injection_regression_gate", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_injection_regression_gate", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_injection_regression_gate", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_injection_regression_gate", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_injection_regression_gate", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_injection_regression_gate", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_injection_regression_gate", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_injection_regression_gate", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_injection_regression_gate", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_injection_regression_gate", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_injection_regression_gate", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_injection_regression_gate", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_injection_regression_gate", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_injection_regression_gate", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_injection_regression_gate", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_injection_regression_gate", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_injection_regression_gate", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_injection_regression_gate", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_injection_regression_gate", "exec_snapshot_link")


class TestInjectionRegressionGate:
    """Test injection regression gate functionality."""

    def test_regression_triggers_fail_closed_attack_success_rate(self):
        from agentic_core.L5_safety.security.injection_regression_gate import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """Test that attack success rate regression triggers fail-closed."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 5,
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.20,  # 10% increase
            "high_risk_count": 5,
            "certification_hash": "current_hash",
        }

        thresholds = RegressionThresholds(
            max_attack_success_rate_increase=0.05,  # 5% threshold
            max_high_risk_count_increase_ratio=0.20,
        )

        with pytest.raises(InjectionRegressionError) as exc_info:
            evaluate_against_baseline(current, baseline, thresholds)

        assert "Attack success rate regression detected" in str(exc_info.value)
        assert "0.10" in str(exc_info.value)
        assert "0.20" in str(exc_info.value)
        assert "0.05" in str(exc_info.value)

    def test_non_regression_passes_attack_success_rate(self):
        """Test that non-regression passes for attack success rate."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 5,
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.14,  # 4% increase
            "high_risk_count": 5,
            "certification_hash": "current_hash",
        }

        thresholds = RegressionThresholds(
            max_attack_success_rate_increase=0.05,  # 5% threshold
            max_high_risk_count_increase_ratio=0.20,
        )

        # Should not raise
        evaluate_against_baseline(current, baseline, thresholds)

    def test_high_risk_count_increase_triggers(self):
        """Test that high-risk count increase triggers regression."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 5,
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.12,  # Within threshold
            "high_risk_count": 6,  # 20% increase (6/5 = 1.2)
            "certification_hash": "current_hash",
        }

        thresholds = RegressionThresholds(
            max_attack_success_rate_increase=0.05,
            max_high_risk_count_increase_ratio=0.15,  # 15% threshold
        )

        with pytest.raises(InjectionRegressionError) as exc_info:
            evaluate_against_baseline(current, baseline, thresholds)

        assert "High-risk count regression detected" in str(exc_info.value)
        assert "baseline=5" in str(exc_info.value)
        assert "current=6" in str(exc_info.value)

    def test_new_high_risk_patterns_with_zero_baseline_fails(self):
        """Test that new high-risk patterns with zero baseline triggers regression."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 0,  # Zero baseline
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.12,
            "high_risk_count": 1,  # New high-risk patterns
            "certification_hash": "current_hash",
        }

        thresholds = RegressionThresholds(
            max_attack_success_rate_increase=0.05, max_high_risk_count_increase_ratio=0.20
        )

        with pytest.raises(InjectionRegressionError) as exc_info:
            evaluate_against_baseline(current, baseline, thresholds)

        assert "High-risk count regression detected" in str(exc_info.value)
        assert "new high-risk patterns introduced" in str(exc_info.value)

    def test_default_thresholds_work(self):
        """Test that default thresholds work without custom configuration."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 5,
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.14,  # Within default 5% threshold
            "high_risk_count": 5,
            "certification_hash": "current_hash",
        }

        # Should not raise with default thresholds
        evaluate_against_baseline(current, baseline)  # No thresholds provided

    def test_check_regression_compliance_function(self):
    """Test check_regression_compliance_function runtime behavior."""
    # Arrange
    # TODO: Set up test data for check_regression_compliance_function
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute check_regression_compliance_function
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            "certification_hash": "current_hash",
        }

        assert check_regression_compliance(current_good, baseline) is True

        # Regression case
        current_bad = {
            "total_samples": 100,
            "attack_success_rate": 0.20,  # Exceeds default threshold
            "high_risk_count": 5,
            "certification_hash": "current_hash",
        }

        assert check_regression_compliance(current_bad, baseline) is False

    def test_edge_case_zero_baseline_zero_current(self):
        """Test edge case with zero baseline and zero current high-risk count."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 0,
            "certification_hash": "baseline_hash",
        }

        current = {
            "total_samples": 100,
            "attack_success_rate": 0.12,
            "high_risk_count": 0,  # Still zero
            "certification_hash": "current_hash",
        }

        # Should not raise - both zero is acceptable
        evaluate_against_baseline(current, baseline)
