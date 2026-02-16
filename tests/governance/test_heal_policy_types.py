"""
Tests for Heal Escalation Policy Types
====================================

CI-grade unit tests for boundary conditions, determinism, and validation.

Tests canonical escalation policy matching execute_ssot.py semantics:
- High confidence (>0.75): proceed deterministically, no LLM
- Medium confidence (0.50..0.75): LLM LOW tier only when enable_llm=True AND judicious gate
- Low confidence (<0.50): LLM HIGH tier only when enable_llm=True AND judicious gate
"""

import pytest

from agentic_core.L5_safety.types.heal_policy_types import (
    ConfidenceLevel,
    HealEscalationInputs,
    LegacyHealEscalationInputs,
    ReasoningTier,
    classify_confidence,
    decide_heal_escalation,
    decide_reasoning_tier,
)

pytestmark = pytest.mark.governance


class TestClassifyConfidence:
    """Test confidence classification at exact boundaries (0.75/0.50 thresholds)."""

    def test_high_boundary(self):
        """Test HIGH threshold at >0.75."""
        assert classify_confidence(0.76) == ConfidenceLevel.HIGH
        assert classify_confidence(0.9) == ConfidenceLevel.HIGH
        assert classify_confidence(1.0) == ConfidenceLevel.HIGH

    def test_high_boundary_exact(self):
        """Test MEDIUM at exactly 0.75 (not > 0.75)."""
        assert classify_confidence(0.75) == ConfidenceLevel.MEDIUM

    def test_medium_boundary(self):
        """Test MEDIUM threshold at 0.50..0.75."""
        assert classify_confidence(0.50) == ConfidenceLevel.MEDIUM
        assert classify_confidence(0.6) == ConfidenceLevel.MEDIUM
        assert classify_confidence(0.74) == ConfidenceLevel.MEDIUM

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


class TestDecideHealEscalation:
    """Test canonical escalation decision matching execute_ssot.py semantics."""

    def test_high_confidence_auto_proceed(self):
        """Test high confidence (>0.75) proceeds without LLM."""
        inputs = HealEscalationInputs(
            confidence_value=0.80,
            enable_llm=False,  # LLM disabled, but should still proceed
            task_complexity=5,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier is None  # No LLM needed
        assert decision.threshold_used == "HIGH_CONF_AUTO"

    def test_high_confidence_boundary_exact(self):
        """Test exactly 0.75 is MEDIUM, not HIGH."""
        inputs = HealEscalationInputs(
            confidence_value=0.75,
            enable_llm=True,
            task_complexity=5,
        )
        decision = decide_heal_escalation(inputs)
        # 0.75 is medium confidence, should use LLM LOW
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "MEDIUM_CONF_LLM_LOW"

    def test_medium_confidence_llm_enabled_judicious_gate_met(self):
        """Test medium confidence with LLM enabled and complexity >= 5."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=True,
            task_complexity=5,  # >= 5 judicious gate
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "MEDIUM_CONF_LLM_LOW"

    def test_medium_confidence_llm_enabled_judicious_gate_not_met(self):
        """Test medium confidence with LLM enabled but complexity < 5."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=True,
            task_complexity=4,  # < 5 judicious gate
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert decision.threshold_used == "MEDIUM_CONF_JUDICIOUS_BLOCK"

    def test_medium_confidence_llm_disabled(self):
        """Test medium confidence with LLM disabled."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=False,
            task_complexity=8,  # High complexity, but LLM disabled
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert decision.threshold_used == "MEDIUM_CONF_LLM_DISABLED"

    def test_low_confidence_llm_enabled_complexity_gate(self):
        """Test low confidence with LLM enabled and complexity >= 7."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=7,  # >= 7 judicious gate
            prior_failures=0,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "LOW_CONF_LLM_HIGH"

    def test_low_confidence_llm_enabled_failure_gate(self):
        """Test low confidence with LLM enabled and prior_failures >= 1."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=3,  # < 7 but failures >= 1
            prior_failures=1,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.HIGH
        assert decision.threshold_used == "LOW_CONF_LLM_HIGH"

    def test_low_confidence_llm_enabled_judicious_gate_not_met(self):
        """Test low confidence with LLM enabled but judicious gate not met."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=5,  # < 7
            prior_failures=0,  # No failures
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert decision.threshold_used == "LOW_CONF_JUDICIOUS_BLOCK"

    def test_low_confidence_llm_disabled(self):
        """Test low confidence with LLM disabled."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=False,
            task_complexity=10,  # High complexity, but LLM disabled
            prior_failures=5,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert decision.threshold_used == "LOW_CONF_LLM_DISABLED"

    def test_determinism(self):
        """Test that same inputs produce identical decisions."""
        inputs = HealEscalationInputs(
            confidence_value=0.65,
            enable_llm=True,
            task_complexity=6,
        )
        decision1 = decide_heal_escalation(inputs)
        decision2 = decide_heal_escalation(inputs)

        assert decision1 == decision2
        assert decision1.proceed == decision2.proceed
        assert decision1.tier == decision2.tier
        assert decision1.rationale == decision2.rationale
        assert decision1.threshold_used == decision2.threshold_used

    def test_validation_confidence_value(self):
        """Test validation of confidence_value field."""
        for invalid in [-0.01, 1.01]:
            inputs = HealEscalationInputs(
                confidence_value=invalid,
                enable_llm=True,
                task_complexity=5,
            )
            with pytest.raises(ValueError, match="confidence_value must be in"):
                decide_heal_escalation(inputs)

    def test_validation_task_complexity(self):
        """Test validation of task_complexity field."""
        for invalid in [-1, 11]:
            inputs = HealEscalationInputs(
                confidence_value=0.8,
                enable_llm=True,
                task_complexity=invalid,
            )
            with pytest.raises(ValueError, match="task_complexity must be in 0..10"):
                decide_heal_escalation(inputs)

    def test_validation_safety_risk(self):
        """Test validation of safety_risk field."""
        for invalid in [-1, 11]:
            inputs = HealEscalationInputs(
                confidence_value=0.8,
                enable_llm=True,
                task_complexity=5,
                safety_risk=invalid,
            )
            with pytest.raises(ValueError, match="safety_risk must be in 0..10"):
                decide_heal_escalation(inputs)

    def test_validation_prior_failures(self):
        """Test validation of prior_failures field."""
        inputs = HealEscalationInputs(
            confidence_value=0.8,
            enable_llm=True,
            task_complexity=5,
            prior_failures=-1,
        )
        with pytest.raises(ValueError, match="prior_failures must be >= 0"):
            decide_heal_escalation(inputs)


class TestDecideReasoningTierLegacy:
    """Test legacy reasoning tier decision logic (backward compatibility)."""

    def test_trivial_rule_returns_low_even_with_low_confidence(self):
        """Test trivial rule applies regardless of confidence."""
        inputs = LegacyHealEscalationInputs(
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
        inputs = LegacyHealEscalationInputs(
            task_complexity=1,  # < 3
            confidence=0.5,  # < 0.75 but trivial should win
            safety_risk=5,  # < 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "TRIVIAL"

    def test_escalation_confidence_low(self):
        """Test escalation due to low confidence (<0.75)."""
        inputs = LegacyHealEscalationInputs(
            task_complexity=5,  # Not trivial
            confidence=0.74,  # < 0.75
            safety_risk=5,  # < 7
            retry_count=1,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.HIGH
        assert "0.75" in decision.threshold_used
        assert "confidence" in decision.rationale.lower()

    def test_escalation_complexity_high(self):
        """Test escalation due to high task complexity."""
        inputs = LegacyHealEscalationInputs(
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
        inputs = LegacyHealEscalationInputs(
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
        inputs = LegacyHealEscalationInputs(
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
        inputs = LegacyHealEscalationInputs(
            task_complexity=5,  # Not < 3
            confidence=0.8,  # >= 0.75
            safety_risk=5,  # < 7
            retry_count=2,  # <= 2
        )

        decision = decide_reasoning_tier(inputs)
        assert decision.tier == ReasoningTier.LOW
        assert decision.threshold_used == "DEFAULT_LOW"
        assert "default" in decision.rationale.lower()

    def test_determinism(self):
        """Test that same inputs produce identical decisions."""
        inputs = LegacyHealEscalationInputs(task_complexity=6, confidence=0.80, safety_risk=4, retry_count=1)

        decision1 = decide_reasoning_tier(inputs)
        decision2 = decide_reasoning_tier(inputs)

        assert decision1 == decision2
        assert decision1.tier == decision2.tier
        assert decision1.rationale == decision2.rationale
        assert decision1.threshold_used == decision2.threshold_used

    def test_validation_task_complexity(self):
        """Test validation of task_complexity field."""
        for valid in [0, 5, 10]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=valid, confidence=0.8, safety_risk=5, retry_count=1
            )
            decide_reasoning_tier(inputs)  # Should not raise

        for invalid in [-1, 11]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=invalid, confidence=0.8, safety_risk=5, retry_count=1
            )
            with pytest.raises(ValueError, match="task_complexity must be in 0..10"):
                decide_reasoning_tier(inputs)

    def test_validation_safety_risk(self):
        """Test validation of safety_risk field."""
        for valid in [0, 5, 10]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=valid, retry_count=1
            )
            decide_reasoning_tier(inputs)  # Should not raise

        for invalid in [-1, 11]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=invalid, retry_count=1
            )
            with pytest.raises(ValueError, match="safety_risk must be in 0..10"):
                decide_reasoning_tier(inputs)

    def test_validation_retry_count(self):
        """Test validation of retry_count field."""
        for valid in [0, 1, 5, 10]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=5, retry_count=valid
            )
            decide_reasoning_tier(inputs)  # Should not raise

        for invalid in [-1, -5]:
            inputs = LegacyHealEscalationInputs(
                task_complexity=5, confidence=0.8, safety_risk=5, retry_count=invalid
            )
            with pytest.raises(ValueError, match="retry_count must be >= 0"):
                decide_reasoning_tier(inputs)
