"""Tests for path_constants healing threshold configuration."""

import unittest


class TestPathConstantsHealingThresholds(unittest.TestCase):
    """Test healing tier thresholds in path_constants."""

    def test_healing_confidence_x_exists(self):
        """HEALING_CONFIDENCE_X must exist and be 0.80."""
        from agentic_core.L0_routing.config.path_constants import HEALING_CONFIDENCE_X

        self.assertEqual(HEALING_CONFIDENCE_X, 0.80)

    def test_healing_confidence_y_exists(self):
        """HEALING_CONFIDENCE_Y must exist and be 0.50."""
        from agentic_core.L0_routing.config.path_constants import HEALING_CONFIDENCE_Y

        self.assertEqual(HEALING_CONFIDENCE_Y, 0.50)

    def test_ssot_score_det_threshold(self):
        """SSOT_SCORE_THRESHOLD_DET must be 13."""
        from agentic_core.L0_routing.config.path_constants import SSOT_SCORE_THRESHOLD_DET

        self.assertEqual(SSOT_SCORE_THRESHOLD_DET, 13)

    def test_ssot_score_qwen_threshold(self):
        """SSOT_SCORE_THRESHOLD_QWEN must be 26."""
        from agentic_core.L0_routing.config.path_constants import SSOT_SCORE_THRESHOLD_QWEN

        self.assertEqual(SSOT_SCORE_THRESHOLD_QWEN, 26)

    def test_qwen_14b_model_id(self):
        """QWEN_14B_MODEL_ID must be correct string."""
        from agentic_core.L0_routing.config.path_constants import QWEN_14B_MODEL_ID

        self.assertEqual(QWEN_14B_MODEL_ID, "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4")

    def test_healing_thresholds_in_all(self):
        """All healing thresholds must be in __all__."""
        from agentic_core.L0_routing.config import path_constants

        self.assertIn("HEALING_CONFIDENCE_X", path_constants.__all__)
        self.assertIn("HEALING_CONFIDENCE_Y", path_constants.__all__)
        self.assertIn("SSOT_SCORE_THRESHOLD_DET", path_constants.__all__)
        self.assertIn("SSOT_SCORE_THRESHOLD_QWEN", path_constants.__all__)
        self.assertIn("QWEN_14B_MODEL_ID", path_constants.__all__)

    def test_threshold_value_constraints(self):
        """Healing thresholds must satisfy X > Y."""
        from agentic_core.L0_routing.config.path_constants import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        self.assertGreater(HEALING_CONFIDENCE_X, HEALING_CONFIDENCE_Y)
        self.assertGreater(HEALING_CONFIDENCE_X, 0.0)
        self.assertGreater(HEALING_CONFIDENCE_Y, 0.0)
        self.assertLess(HEALING_CONFIDENCE_X, 1.0)
        self.assertLess(HEALING_CONFIDENCE_Y, 1.0)


class TestPathConstantsCore(unittest.TestCase):
    """Core path constants functionality."""

    def test_get_validated_project_root(self):
        """Test get_validated_project_root returns non-None path."""
        from agentic_core.L0_routing.config import get_validated_project_root

        result = get_validated_project_root()
        self.assertIsNotNone(result)

    def test_get_apps_directories(self):
        """Test get_apps_directories returns list."""
        from agentic_core.L0_routing.config import get_apps_directories

        result = get_apps_directories()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
