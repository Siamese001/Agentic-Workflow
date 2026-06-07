"""Unit tests for ``agentic_core.L2_execution.reasoning.cost_aware_cascade``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` W8.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.cost_aware_cascade import (
    ProviderConfidenceCalibrator,
    ProviderFingerprintGate,
    ProviderFingerprintMismatchError,
    should_escalate,
)


def test_should_escalate_below_safety_floor_always_true() -> None:
    assert should_escalate(
        current_confidence=0.20,
        expected_gain_at_higher_tier=0.0,
        tier_cost_delta=1.0,
        safety_floor=0.40,
    ) is True


def test_should_escalate_above_floor_uses_utility() -> None:
    # Gain (0.30) > cost (0.20) → escalate
    assert should_escalate(
        current_confidence=0.50,
        expected_gain_at_higher_tier=0.30,
        tier_cost_delta=0.20,
    ) is True
    # Gain (0.10) < cost (0.20) → stay
    assert should_escalate(
        current_confidence=0.50,
        expected_gain_at_higher_tier=0.10,
        tier_cost_delta=0.20,
    ) is False


def test_should_escalate_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        should_escalate(
            current_confidence=1.5,
            expected_gain_at_higher_tier=0.1,
            tier_cost_delta=0.1,
        )
    with pytest.raises(ValueError):
        should_escalate(
            current_confidence=0.5,
            expected_gain_at_higher_tier=2.0,
            tier_cost_delta=0.1,
        )


def test_fingerprint_gate_first_provider_binds_silently() -> None:
    gate = ProviderFingerprintGate()
    gate.verify("openai/gpt-4", "fp_a")  # binds
    # Same fingerprint on second call → no raise
    gate.verify("openai/gpt-4", "fp_a")


def test_fingerprint_gate_drift_raises() -> None:
    gate = ProviderFingerprintGate()
    gate.bind_snapshot("openai/gpt-4", "fp_a")
    with pytest.raises(ProviderFingerprintMismatchError):
        gate.verify("openai/gpt-4", "fp_b")


def test_fingerprint_gate_independent_per_provider() -> None:
    gate = ProviderFingerprintGate()
    gate.bind_snapshot("openai/gpt-4", "fp_a")
    gate.bind_snapshot("anthropic/claude", "fp_x")
    gate.verify("openai/gpt-4", "fp_a")
    gate.verify("anthropic/claude", "fp_x")


def test_calibrator_demotes_chronic_overconfident_provider() -> None:
    cal = ProviderConfidenceCalibrator(brier_demote_threshold=0.30, min_observations=20)
    # Provider claims 0.95 success but actual rate is 0%
    for _ in range(25):
        cal.observe("flaky_provider", predicted_success=0.95, actual_success=False)
    stats = cal.stats("flaky_provider")
    assert stats.n_observations == 25
    # (0.95 - 0)^2 = 0.9025 → far above 0.30
    assert stats.brier_score > 0.30
    assert stats.demoted is True
    assert "flaky_provider" in cal.demoted_providers()


def test_calibrator_no_demote_when_well_calibrated() -> None:
    cal = ProviderConfidenceCalibrator(brier_demote_threshold=0.30, min_observations=20)
    for _ in range(25):
        cal.observe("good_provider", predicted_success=0.85, actual_success=True)
    stats = cal.stats("good_provider")
    # (0.85 - 1)^2 = 0.0225 → well below 0.30
    assert stats.brier_score < 0.30
    assert stats.demoted is False


def test_calibrator_no_demote_when_insufficient_data() -> None:
    cal = ProviderConfidenceCalibrator(brier_demote_threshold=0.10, min_observations=50)
    for _ in range(10):
        cal.observe("new_provider", predicted_success=0.9, actual_success=False)
    stats = cal.stats("new_provider")
    assert stats.brier_score > 0.10
    assert stats.demoted is False


def test_calibrator_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        ProviderConfidenceCalibrator(brier_demote_threshold=1.5)
    with pytest.raises(ValueError):
        ProviderConfidenceCalibrator(min_observations=0)


def test_calibrator_unknown_provider_returns_blank_stats() -> None:
    cal = ProviderConfidenceCalibrator()
    stats = cal.stats("never_seen")
    assert stats.n_observations == 0
    assert stats.brier_score == 0.0
    assert stats.demoted is False
