"""
Tests for Injection Regression Gate - Guardian Security Tests.

Tests fail-closed regression detection for injection security.
All tests are deterministic and use in-memory fixtures.
"""

import pytest

from agentic_core.L5_safety.security.injection_regression_gate import (
    InjectionRegressionError,
    RegressionThresholds,
    check_regression_compliance,
    evaluate_against_baseline,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_injection_regression_gate")
_emit_applies_guardrail("p0", "test_injection_regression_gate", "p0_governance")
_emit_reads_policy_state("p0", "test_injection_regression_gate", "policy_binding")
_emit_snapshots_state("p0", "test_injection_regression_gate", "state_snapshot")
emit_replay_key("p0", "test_injection_regression_gate")
emit_determinism_digest("p0", "test_injection_regression_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_injection_regression_gate", "execution_auth")
_emit_validates_capability("p2", "test_injection_regression_gate", "capability_check")
_emit_routes_to_capability("p2", "test_injection_regression_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_injection_regression_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_injection_regression_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_injection_regression_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_injection_regression_gate", "exec_output")
_emit_dispatches_agent("p3", "test_injection_regression_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_injection_regression_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_injection_regression_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_injection_regression_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_injection_regression_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_injection_regression_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_injection_regression_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_injection_regression_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_injection_regression_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_injection_regression_gate", "eval_metric")
_emit_stores_embedding("p4", "test_injection_regression_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_injection_regression_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_injection_regression_gate", "exec_snapshot_link")


class TestInjectionRegressionGate:
    """Test injection regression gate functionality."""

    def test_regression_triggers_fail_closed_attack_success_rate(self):
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
        """Test the check_regression_compliance helper function."""
        baseline = {
            "total_samples": 100,
            "attack_success_rate": 0.10,
            "high_risk_count": 5,
            "certification_hash": "baseline_hash",
        }

        # Non-regression case
        current_good = {
            "total_samples": 100,
            "attack_success_rate": 0.12,
            "high_risk_count": 5,
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
