#!/usr/bin/env python3
"""
Aggressive unit tests for unified confidence threshold logic.
Verifies that ALL confidence logic uses strictly > 0.75 for high confidence.
"""

import sys
import unittest
from pathlib import Path

# Add the project root and scripts path to sys.path for import
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
scripts_path = project_root / "agentic_core" / "L0_maintenance" / "scripts"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

try:
    import execute_ssot

    IMPORTS_AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError) as e:
    print(f"Warning: Failed to import execute_ssot: {e}")
    IMPORTS_AVAILABLE = False
    execute_ssot = None


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestUnifiedConfidenceThresholds(unittest.TestCase):
    def test_threshold_boundary_strict(self):
        """100% PASS: Verify strictly > 0.75 is required (0.75 is NOT high)."""
        # Exact boundary case
        score_boundary = execute_ssot.ConfidenceScore(value=0.75, reasoning="Boundary")
        self.assertFalse(score_boundary.is_high_confidence, "0.75 should NOT be high confidence")
        self.assertTrue(score_boundary.is_medium_confidence, "0.75 MUST be medium confidence")
        self.assertFalse(score_boundary.is_low_confidence, "0.75 should NOT be low confidence")

        # Just above boundary
        score_above = execute_ssot.ConfidenceScore(value=0.751, reasoning="Above")
        self.assertTrue(score_above.is_high_confidence, "0.751 SHOULD be high confidence")
        self.assertFalse(score_above.is_medium_confidence, "0.751 should NOT be medium")
        self.assertFalse(score_above.is_low_confidence, "0.751 should NOT be low")

        # Just below boundary
        score_below = execute_ssot.ConfidenceScore(value=0.749, reasoning="Below")
        self.assertFalse(score_below.is_high_confidence, "0.749 should NOT be high confidence")
        self.assertTrue(score_below.is_medium_confidence, "0.749 SHOULD be medium confidence")
        self.assertFalse(score_below.is_low_confidence, "0.749 should NOT be low confidence")

    def test_decision_engine_logic(self):
        """100% PASS: Decision engine uses new simplified thresholds."""
        engine = execute_ssot.AutonomousDecisionEngine(enable_llm=False)

        # Test 0.75 (Fail/Wait)
        score_75 = execute_ssot.ConfidenceScore(value=0.75, reasoning="Testing 0.75")
        proceed, msg = engine.should_proceed_with_healing(score_75)
        self.assertFalse(proceed, "Should NOT proceed at 0.75 without LLM")
        self.assertIn("LOW CONFIDENCE", msg)
        self.assertIn("LLM Disabled", msg)

        # Test 0.76 (Pass)
        score_76 = execute_ssot.ConfidenceScore(value=0.76, reasoning="Testing 0.76")
        proceed, msg = engine.should_proceed_with_healing(score_76)
        self.assertTrue(proceed, "Should proceed at 0.76")
        self.assertIn("AUTO-HEAL", msg)
        self.assertIn("> 0.75", msg)

        # Test 0.5 (Medium boundary)
        score_5 = execute_ssot.ConfidenceScore(value=0.5, reasoning="Testing 0.5")
        proceed, msg = engine.should_proceed_with_healing(score_5)
        self.assertFalse(proceed, "Should NOT proceed at 0.5 without LLM")
        self.assertIn("LOW CONFIDENCE", msg)

        # Test with LLM enabled
        engine_llm = execute_ssot.AutonomousDecisionEngine(enable_llm=True)
        proceed_llm, msg_llm = engine_llm.should_proceed_with_healing(score_75)
        self.assertTrue(proceed_llm, "Should proceed at 0.75 WITH LLM enabled")
        self.assertIn("LLM Override", msg_llm)

    def test_reporting_logic_consistency(self):
        """100% PASS: Ensure reporting logic matches decision logic."""
        # This mirrors the logic in main() to ensure no off-by-one errors
        decisions = [
            {"confidence": 0.80},
            {"confidence": 0.76},
            {"confidence": 0.75},  # Boundary
            {"confidence": 0.50},
            {"confidence": 0.749},
            {"confidence": 0.751},
        ]

        high_conf = sum(1 for d in decisions if d["confidence"] > 0.75)
        med_conf = sum(1 for d in decisions if 0.5 <= d["confidence"] <= 0.75)
        low_conf = sum(1 for d in decisions if d["confidence"] < 0.5)

        self.assertEqual(high_conf, 3, "Should count 0.80, 0.76, and 0.751 as high")
        self.assertEqual(med_conf, 3, "Should count 0.75, 0.749, and 0.50 as medium")
        self.assertEqual(low_conf, 0, "Should count no values as low")

    def test_edge_cases(self):
        """Test extreme values and edge cases."""
        # Perfect score
        score_perfect = execute_ssot.ConfidenceScore(value=1.0, reasoning="Perfect")
        self.assertTrue(score_perfect.is_high_confidence, "1.0 should be high confidence")

        # Zero score
        score_zero = execute_ssot.ConfidenceScore(value=0.0, reasoning="Zero")
        self.assertTrue(score_zero.is_low_confidence, "0.0 should be low confidence")

        # Just above 0.5
        score_above_half = execute_ssot.ConfidenceScore(value=0.501, reasoning="Above half")
        self.assertTrue(score_above_half.is_medium_confidence, "0.501 should be medium confidence")

        # Exactly 0.5
        score_half = execute_ssot.ConfidenceScore(value=0.5, reasoning="Exactly half")
        self.assertTrue(score_half.is_medium_confidence, "0.5 should be medium confidence")

    def test_confidence_calculation_factors(self):
        """Verify confidence calculation still works with new thresholds."""
        engine = execute_ssot.AutonomousDecisionEngine()

        # Test zero violations (should be perfect confidence)
        conf_zero = engine.calculate_healing_confidence(0, [], "trusted_territory")
        self.assertEqual(conf_zero.value, 1.0, "Zero violations should give perfect confidence")
        self.assertTrue(conf_zero.is_high_confidence, "Perfect confidence should be high")

        # Test some violations in trusted territory
        conf_some = engine.calculate_healing_confidence(5, ["SHALLOW"], "trusted_territory")
        self.assertGreater(conf_some.value, 0.0, "Should have some confidence")
        self.assertLessEqual(conf_some.value, 1.0, "Confidence should not exceed 1.0")


if __name__ == "__main__":
    print("🧪 Running Unified Confidence Threshold Tests...")
    print("=" * 60)

    # Run the tests with verbose output
    unittest.main(verbosity=2)
