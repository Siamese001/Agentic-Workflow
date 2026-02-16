"""
Tests for Heal Escalation Policy Types
====================================

CI-grade unit tests for boundary conditions, determinism, and validation.
"""

import pytest

from agentic_core.L5_safety.types.heal_policy_types import (
    ConfidenceLevel,
    HealEscalationInputs,
    ReasoningTier,
    classify_confidence,
    decide_reasoning_tier,
)

pytestmark = pytest.mark.governance


class TestClassifyConfidence:
    """Test confidence classification at exact boundaries."""

    def test_very_high_boundary(self):
        """Test VERY_HIGH threshold at 0.85."""
        assert classify_confidence(0.85) == ConfidenceLevel.VERY_HIGH
        assert classify_confidence(0.9) == ConfidenceLevel.VERY_HIGH
        assert classify_confidence(1.0) == ConfidenceLevel.VERY_HIGH

    def test_very_high_boundary_just_below(self):
        """Test HIGH at 0.849999 (just below VERY_HIGH threshold)."""
        assert classify_confidence(0.849999) == ConfidenceLevel.HIGH

    def test_high_boundary(self):
        """Test HIGH threshold at 0.70."""
        assert classify_confidence(0.70) == ConfidenceLevel.HIGH
        assert classify_confidence(0.8) == ConfidenceLevel.HIGH

    def test_high_boundary_just_below(self):
        """Test MEDIUM at 0.699999 (just below HIGH threshold)."""
        assert classify_confidence(0.699999) == ConfidenceLevel.MEDIUM

    def test_medium_boundary(self):
        """Test MEDIUM threshold at 0.50."""
        assert classify_confidence(0.50) == ConfidenceLevel.MEDIUM
        assert classify_confidence(0.6) == ConfidenceLevel.MEDIUM

    def test_medium_boundary_just_below(self):
        """Test LOW at 0.499999 (just below MEDIUM threshold)."""
        assert classify_confidence(0.499999) == ConfidenceLevel.LOW

    def test_low_values(self):
        """Test LOW for values below 0.50."""
        assert classify_confidence(0.0) == ConfidenceLevel.LOW
        assert classify_confidence(0.25) == ConfidenceLevel.LOW
        assert classify_confidence(0.49) == ConfidenceLevel.LOW

    def test_validation_errors(self):
        """Test ValueError for out-of-range confidence values."""
        with pytest.raises(ValueError, match="Confidence must be in \\[0.0, 1.0\\]"):
            classify_confidence(-0.01)

        with pytest.raises(ValueError, match="Confidence must be in \\[0.0, 1.0\\]"):
            classify_confidence(1.01)


class TestDecideReasoningTier:
    """Test reasoning tier decision logic."""

    def test_trivial_rule_returns_low_even_with_low_confidence(self):
        """Test trivial rule applies regardless of confidence."""
        # Even with very low confidence, trivial rule should return LOW
        inputs = HealEscalationInputs(
            task_complexity=2,  # < 3
            confidence=0.1,  # Very low
            safety_risk=6,  # < 7
            retry_count=2,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "TRIVIAL"
        assert "trivial" in decision.rationale.lower()

    def test_trivial_rule_order(self):
        """Test that trivial rule is checked before escalation rules."""
        # This should use TRIVIAL rule, not CONF_LT_0.70 rule
        inputs = HealEscalationInputs(
            task_complexity=1,  # < 3
            confidence=0.5,  # < 0.70 but trivial should win
            safety_risk=5,  # < 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "TRIVIAL"

    def test_escalation_confidence_low(self):
        """Test escalation due to low confidence."""
        inputs = HealEscalationInputs(
            task_complexity=5,  # Not trivial
            confidence=0.69,  # < 0.70
            safety_risk=5,  # < 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "CONF_LT_0.70"
        assert "confidence" in decision.rationale.lower()

    def test_escalation_complexity_high(self):
        """Test escalation due to high task complexity."""
        inputs = HealEscalationInputs(
            task_complexity=8,  # >= 8
            confidence=0.8,  # High confidence
            safety_risk=5,  # < 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "COMPLEXITY_GE_8"
        assert "complexity" in decision.rationale.lower()

    def test_escalation_safety_risk_high(self):
        """Test escalation due to high safety risk."""
        inputs = HealEscalationInputs(
            task_complexity=5,  # Not trivial
            confidence=0.8,  # High confidence
            safety_risk=7,  # >= 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "SAFETY_GE_7"
        assert "safety" in decision.rationale.lower()

    def test_escalation_retry_count_high(self):
        """Test escalation due to high retry count."""
        inputs = HealEscalationInputs(
            task_complexity=5,  # Not trivial
            confidence=0.8,  # High confidence
            safety_risk=5,  # < 7
            retry_count=3,  # > 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "RETRY_GT_2"
        assert "retries" in decision.rationale.lower()

    def test_default_low(self):
        """Test default LOW when no escalation triggers met."""
        inputs = HealEscalationInputs(
            task_complexity=5,  # Not < 3
            confidence=0.8,  # >= 0.70
            safety_risk=5,  # < 7
            retry_count=2,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "DEFAULT_LOW"
        assert "default" in decision.rationale.lower()

    def test_determinism(self):
        """Test that same inputs produce identical decisions."""
        inputs = HealEscalationInputs(task_complexity=6, confidence=0.75, safety_risk=4, retry_count=1)

        decision1 = decide_reasoning_tier(inputs)
        decision2 = decide_reasoning_tier(inputs)

        # Objects should be equal
        assert decision1 == decision2

        # All fields should be identical
        assert decision1.tier == decision2.tier
        assert decision1.rationale == decision2.rationale
        assert decision1.threshold_used == decision2.threshold_used

    def test_validation_task_complexity(self):
        """Test validation of task_complexity field."""
        # Valid values
        for valid in [0, 5, 10]:
            inputs = HealEscalationInputs(task_complexity=valid, confidence=0.8, safety_risk=5, retry_count=1)
            decide_reasoning_tier(inputs)  # Should not raise

        # Invalid values
        for invalid in [-1, 11]:
            inputs = HealEscalationInputs(
                task_complexity=invalid, confidence=0.8, safety_risk=5, retry_count=1
            )
            with pytest.raises(ValueError, match="task_complexity must be in 0..10"):
                decide_reasoning_tier(inputs)

    def test_validation_safety_risk(self):
        """Test validation of safety_risk field."""
        # Valid values
        for valid in [0, 5, 10]:
            inputs = HealEscalationInputs(task_complexity=5, confidence=0.8, safety_risk=valid, retry_count=1)
            decide_reasoning_tier(inputs)  # Should not raise

        # Invalid values
        for invalid in [-1, 11]:
            inputs = HealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=invalid, retry_count=1
            )
            with pytest.raises(ValueError, match="safety_risk must be in 0..10"):
                decide_reasoning_tier(inputs)

    def test_validation_retry_count(self):
        """Test validation of retry_count field."""
        # Valid values
        for valid in [0, 1, 5, 10]:
            inputs = HealEscalationInputs(task_complexity=5, confidence=0.8, safety_risk=5, retry_count=valid)
            decide_reasoning_tier(inputs)  # Should not raise

        # Invalid values
        for invalid in [-1, -5]:
            inputs = HealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=5, retry_count=invalid
            )
            with pytest.raises(ValueError, match="retry_count must be >= 0"):
                decide_reasoning_tier(inputs)
