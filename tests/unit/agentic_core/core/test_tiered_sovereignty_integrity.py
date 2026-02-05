import os
import unittest
from unittest.mock import patch

from agentic_core.L0_maintenance.scripts.general_scripts.execute_ssot import (
    ConfidenceScore,
    SovereignDecisionEngine,
)


class TestTieredSovereigntyIntegrity(unittest.TestCase):
    """
    Mandatory 100% pass for tiered model and threshold logic.
    Ensures .env variables drive all autonomous healing gates.
    """

    @patch.dict(
        os.environ,
        {
            "SOVEREIGN_HIGH_CONFIDENCE": "0.85",
            "SOVEREIGN_MEDIUM_CONFIDENCE": "0.45",
            "GEMINI_MODEL": "test-flash-v3",
            "GEMINI_PRO_MODEL": "test-pro-v2",
        },
    )
    def test_dynamic_threshold_resolution(self):
        """Case 1: Verify 0.80 is treated as Medium when High threshold is 0.85."""
        score = ConfidenceScore(value=0.80, reasoning="Edge Case")
        self.assertTrue(score.is_medium_confidence)
        self.assertFalse(score.is_high_confidence)

    @patch.dict(os.environ, {"GEMINI_MODEL": "test-flash-v3", "GEMINI_PRO_MODEL": "test-pro-v2"})
    def test_model_assignment_parity(self):
        """Case 2: Verify correct model assignment for arbitration vs recovery."""
        engine = SovereignDecisionEngine(enable_llm=True)

        # Test Medium (Flash)
        conf_med = ConfidenceScore(value=0.60, reasoning="Test")
        engine.should_proceed_with_healing(conf_med, "AgentA")
        self.assertEqual(engine.decisions_made[-1]["model"], "test-flash-v3")

        # Test Low (Pro)
        conf_low = ConfidenceScore(value=0.30, reasoning="Test")
        engine.should_proceed_with_healing(conf_low, "AgentB")
        self.assertEqual(engine.decisions_made[-1]["model"], "test-pro-v2")

    @patch.dict(
        os.environ, {"SOVEREIGN_HIGH_CONFIDENCE": "0.90", "SOVEREIGN_MEDIUM_CONFIDENCE": "0.60"}
    )
    def test_custom_threshold_boundaries(self):
        """Case 3: Test boundary conditions with custom thresholds."""
        # Test exact boundary values
        high_boundary = ConfidenceScore(value=0.90, reasoning="High boundary")
        self.assertFalse(high_boundary.is_high_confidence)  # Should be False since it's >, not >=
        self.assertTrue(high_boundary.is_medium_confidence)

        med_boundary_high = ConfidenceScore(value=0.60, reasoning="Med high boundary")
        self.assertTrue(med_boundary_high.is_medium_confidence)
        self.assertFalse(med_boundary_high.is_low_confidence)

        med_boundary_low = ConfidenceScore(value=0.60, reasoning="Med low boundary")
        self.assertTrue(med_boundary_low.is_medium_confidence)
        self.assertFalse(med_boundary_low.is_low_confidence)

        low_boundary = ConfidenceScore(value=0.60, reasoning="Low boundary")
        self.assertFalse(low_boundary.is_low_confidence)  # Should be False since it's <, not <=

    def test_default_threshold_fallback(self):
        """Case 4: Verify default thresholds when environment variables are not set."""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            score = ConfidenceScore(value=0.80, reasoning="Default test")

            # Should use default values: HIGH=0.75, MEDIUM=0.50
            self.assertTrue(score.is_high_confidence)  # 0.80 > 0.75
            self.assertFalse(score.is_medium_confidence)
            self.assertFalse(score.is_low_confidence)

            score_med = ConfidenceScore(value=0.60, reasoning="Default med test")
            self.assertFalse(score_med.is_high_confidence)  # 0.60 <= 0.75
            self.assertTrue(score_med.is_medium_confidence)  # 0.60 >= 0.50 and <= 0.75
            self.assertFalse(score_med.is_low_confidence)  # 0.60 >= 0.50

    @patch.dict(
        os.environ, {"GEMINI_MODEL": "custom-flash-model", "GEMINI_PRO_MODEL": "custom-pro-model"}
    )
    def test_model_fallback_values(self):
        """Case 5: Test model fallback when environment variables are set."""
        engine = SovereignDecisionEngine(enable_llm=True)

        # Test Medium confidence with custom model
        conf_med = ConfidenceScore(value=0.60, reasoning="Test")
        success, reason = engine.should_proceed_with_healing(conf_med, "AgentA")
        self.assertTrue(success)
        # Check that the model is stored in the decision data, not the reason string
        self.assertEqual(engine.decisions_made[-1]["model"], "custom-flash-model")

        # Test Low confidence with custom model
        conf_low = ConfidenceScore(value=0.30, reasoning="Test")
        success, reason = engine.should_proceed_with_healing(conf_low, "AgentB")
        self.assertTrue(success)
        self.assertEqual(engine.decisions_made[-1]["model"], "custom-pro-model")


if __name__ == "__main__":
    unittest.main()
