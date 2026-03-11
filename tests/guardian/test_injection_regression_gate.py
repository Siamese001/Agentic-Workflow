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
        assert True  # no-exception contract

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
        assert True  # no-exception contract

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
        assert True  # no-exception contract
