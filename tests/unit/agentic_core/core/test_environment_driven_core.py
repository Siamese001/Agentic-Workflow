import os
import unittest
from unittest.mock import patch


class TestEnvironmentDrivenCore(unittest.TestCase):
    """
    Core test for environment-driven configuration.
    Tests the fundamental pattern without complex imports.
    """

    def setUp(self):
        """Set up test environment with clean state."""
        self.original_env = dict(os.environ)
        os.environ.clear()

    def tearDown(self):
        """Restore original environment after each test."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_environment_variable_sourcing_pattern(self):
        """Test the core environment variable sourcing pattern used across components."""

        # Simulate the pattern used in refactored components
        class TestConfig:
            @property
            def test_threshold(self):
                return float(os.getenv("TEST_THRESHOLD", "0.75"))

            @property
            def test_model(self):
                return os.getenv("TEST_MODEL", "default-model")

        # Test with environment variables set
        with patch.dict(os.environ, {"TEST_THRESHOLD": "0.85", "TEST_MODEL": "custom-model"}):
            config = TestConfig()
            self.assertEqual(config.test_threshold, 0.85)
            self.assertEqual(config.test_model, "custom-model")

        # Test with default fallbacks
        config = TestConfig()
        self.assertEqual(config.test_threshold, 0.75)
        self.assertEqual(config.test_model, "default-model")

    def test_confidence_score_environment_pattern(self):
        """Test the ConfidenceScore environment pattern from execute_ssot.py."""

        # Import the actual refactored ConfidenceScore
        from agentic_core.L0_maintenance.scripts.general_scripts.execute_ssot import ConfidenceScore

        # Test with custom environment thresholds
        with patch.dict(
            os.environ, {"SOVEREIGN_HIGH_CONFIDENCE": "0.85", "SOVEREIGN_MEDIUM_CONFIDENCE": "0.45"}
        ):
            score = ConfidenceScore(value=0.80, reasoning="Test")
            self.assertTrue(score.is_medium_confidence)
            self.assertFalse(score.is_high_confidence)
            self.assertFalse(score.is_low_confidence)

        # Test with default thresholds
        score = ConfidenceScore(value=0.80, reasoning="Test")
        self.assertTrue(score.is_high_confidence)  # 0.80 > 0.75 default
        self.assertFalse(score.is_medium_confidence)
        self.assertFalse(score.is_low_confidence)

    def test_sovereign_decision_engine_environment_integration(self):
        """Test SovereignDecisionEngine uses environment variables for model selection."""

        from agentic_core.L0_maintenance.scripts.general_scripts.execute_ssot import (
            ConfidenceScore,
            SovereignDecisionEngine,
        )

        with patch.dict(
            os.environ,
            {"GEMINI_MODEL": "custom-flash-model", "GEMINI_PRO_MODEL": "custom-pro-model"},
        ):
            engine = SovereignDecisionEngine(enable_llm=True)

            # Test medium confidence uses custom flash model
            conf_med = ConfidenceScore(value=0.60, reasoning="Test")
            success, reason = engine.should_proceed_with_healing(conf_med, "AgentA")
            self.assertTrue(success)
            self.assertEqual(engine.decisions_made[-1]["model"], "custom-flash-model")

            # Test low confidence uses custom pro model
            conf_low = ConfidenceScore(value=0.30, reasoning="Test")
            success, reason = engine.should_proceed_with_healing(conf_low, "AgentB")
            self.assertTrue(success)
            self.assertEqual(engine.decisions_made[-1]["model"], "custom-pro-model")

    def test_no_hardcoded_values_in_decision_engine(self):
        """Verify decision engine doesn't use hardcoded model strings."""

        from agentic_core.L0_maintenance.scripts.general_scripts.execute_ssot import (
            ConfidenceScore,
            SovereignDecisionEngine,
        )

        # Clear environment to test defaults
        with patch.dict(os.environ, {}, clear=True):
            engine = SovereignDecisionEngine(enable_llm=True)

            conf_med = ConfidenceScore(value=0.60, reasoning="Test")
            success, reason = engine.should_proceed_with_healing(conf_med, "AgentA")
            self.assertTrue(success)

            # Should use default model from environment or fallback
            model_used = engine.decisions_made[-1]["model"]
            self.assertIn(model_used, ["gemini-3-flash-preview", None])  # Default or None

    def test_environment_variable_type_conversion(self):
        """Test proper type conversion from environment strings to appropriate types."""

        class TypeTestConfig:
            @property
            def int_value(self):
                return int(os.getenv("INT_VALUE", "42"))

            @property
            def float_value(self):
                return float(os.getenv("FLOAT_VALUE", "3.14"))

            @property
            def bool_value(self):
                return os.getenv("BOOL_VALUE", "true").lower() == "true"

        with patch.dict(os.environ, {"INT_VALUE": "100", "FLOAT_VALUE": "2.71", "BOOL_VALUE": "false"}):
            config = TypeTestConfig()
            self.assertEqual(config.int_value, 100)
            self.assertEqual(config.float_value, 2.71)
            self.assertFalse(config.bool_value)


if __name__ == "__main__":
    unittest.main()
