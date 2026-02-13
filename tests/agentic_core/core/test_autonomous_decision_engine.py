import sys
from pathlib import Path

import pytest

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine


def test_trusted_territory_mass_edit_confidence():
    """Test 1: Verify 100 violations in 'prompt_governance' (Trusted) yields High Confidence."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    # 100 Naming violations in Trusted territory
    score = engine.calculate_healing_confidence(
        violations_count=100,
        violation_types=["NAMING", "STRUCTURE"],
        territory="prompt_governance",
    )

    # Calculation Estimate:
    # Count (<=100, Trusted): 0.85 * 0.35 = 0.2975
    # Types (Known):          1.00 * 0.25 = 0.2500
    # Hist (0.9):             0.90 * 0.15 = 0.1350
    # Complexity (Trusted):   1.00 * 0.25 = 0.2500
    # Total: ~0.93 (High Confidence)

    print(f"\nTrusted Score: {score.value} ({score.reasoning})")
    assert score.is_high_confidence is True
    assert score.value > 0.85
    print("Test Case 1: 100% pass - Trusted Velocity Verified")


def test_critical_territory_caution():
    """Test 2: Verify same 100 violations in 'L5_safety' (Critical) yields Low/Medium Confidence."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    # 100 Naming violations in Critical territory
    score = engine.calculate_healing_confidence(
        violations_count=100,
        violation_types=["NAMING"],
        territory="L5_safety",
    )

    # Calculation Estimate:
    # Count (<=100, Critical): 0.40 * 0.35 = 0.140
    # Types (Known):           1.00 * 0.25 = 0.250
    # Hist (0.9):              0.90 * 0.15 = 0.135
    # Complexity (Critical):   0.60 * 0.25 = 0.150
    # Total: ~0.675 (Medium Confidence)

    print(f"Critical Score: {score.value} ({score.reasoning})")
    assert score.is_high_confidence is False
    assert score.is_medium_confidence is True
    print("Test Case 2: 100% pass - Critical Guardrails Verified")


def test_unknown_violation_types_penalty():
    """Test 3: Verify unknown violation types tank confidence even in trusted zones."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    score = engine.calculate_healing_confidence(
        violations_count=10,
        violation_types=["ALIEN_INVASION", "UNKNOWN_ERROR"],
        territory="prompt_governance",
    )

    # Known Types factor should drop to 0.5
    assert score.factors["known_types"] == 0.5
    print("Test Case 3: 100% pass - Anomaly Detection Verified")


def test_standard_territory_behavior():
    """Test 4: Verify 'apps_shared' falls into Standard profile."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    score = engine.calculate_healing_confidence(
        violations_count=20,
        violation_types=["IMPORT"],
        territory="agentic_core/some_new_feature",
    )

    assert "STANDARD" in score.reasoning
    print("Test Case 4: 100% pass - Standard Profile Verified")


def test_trusted_territory_mass_edit_with_llm_override():
    """Test 5: Verify trusted zones maintain high confidence even with mass edits."""
    engine = AutonomousDecisionEngine(enable_llm=True)

    # Use violation count that would normally be concerning
    score = engine.calculate_healing_confidence(
        violations_count=200,
        violation_types=["NAMING"],
        territory="scripts",
    )

    # Should still be high confidence (trusted zones are very resilient)
    assert score.is_high_confidence is True

    # Should proceed with high confidence
    proceed, reason = engine.should_proceed_with_healing(score)
    assert proceed is True
    assert "HIGH CONFIDENCE" in reason
    print("Test Case 5: 100% pass - Trusted Zone High Confidence Maintained")


def test_critical_territory_no_llm_override():
    """Test 6: Verify critical zones reject low confidence without LLM."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    # Extreme violation count in critical territory to force low confidence
    score = engine.calculate_healing_confidence(
        violations_count=500,
        violation_types=["NAMING", "UNKNOWN_ERROR"],
        territory="L5_safety",
    )

    # Should be low confidence with extreme violations and unknown types
    assert score.is_low_confidence is True

    # Should be rejected without LLM
    proceed, reason = engine.should_proceed_with_healing(score)
    assert proceed is False
    assert "LLM Disabled" in reason
    print("Test Case 6: 100% pass - Critical Zone Rejection Verified")


def test_all_trusted_territories():
    """Test 7: Verify all trusted territories get trust bonus."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    trusted_territories = [
        "prompt_governance",
        "scripts",
        "tests",
        "L0_maintenance",
        "apps_lic",
        "apps_rg",
    ]

    for territory in trusted_territories:
        score = engine.calculate_healing_confidence(
            violations_count=50,
            violation_types=["NAMING"],
            territory=territory,
        )

        assert "TRUSTED" in score.reasoning
        assert score.factors["territory_complexity"] == 1.0

    print("Test Case 7: 100% pass - All Trusted Territories Verified")


def test_all_critical_territories():
    """Test 8: Verify all critical territories get caution penalty."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    critical_territories = ["L5_safety", "L3_orchestration", "base_agents", "L2_execution"]

    for territory in critical_territories:
        score = engine.calculate_healing_confidence(
            violations_count=50,
            violation_types=["NAMING"],
            territory=territory,
        )

        assert "CRITICAL" in score.reasoning
        assert score.factors["territory_complexity"] == 0.6

    print("Test Case 8: 100% pass - All Critical Territories Verified")


def test_zero_violations_always_high_confidence():
    """Test 9: Verify zero violations always yield high confidence regardless of territory."""
    engine = AutonomousDecisionEngine(enable_llm=False)

    territories = ["prompt_governance", "L5_safety", "agentic_core/random"]

    for territory in territories:
        score = engine.calculate_healing_confidence(
            violations_count=0,
            violation_types=[],
            territory=territory,
        )

        assert score.is_high_confidence is True
        assert score.value >= 0.8  # High confidence threshold
        assert score.factors["violation_count"] == 1.0

    print("Test Case 9: 100% pass - Zero Violations Always High Confidence")


def test_decision_audit_trail():
    """Test 10: Verify decisions are properly recorded in audit trail."""
    engine = AutonomousDecisionEngine(enable_llm=True)

    score = engine.calculate_healing_confidence(
        violations_count=10,
        violation_types=["NAMING"],
        territory="prompt_governance",
    )

    # Make a decision
    proceed, reason = engine.should_proceed_with_healing(score)

    # Verify audit trail
    assert len(engine.decisions_made) == 1
    decision = engine.decisions_made[0]

    assert "confidence" in decision
    assert "timestamp" in decision
    assert "decision" in decision
    assert "reason" in decision
    assert decision["decision"] == proceed
    assert decision["reason"] == reason

    print("Test Case 10: 100% pass - Decision Audit Trail Verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
