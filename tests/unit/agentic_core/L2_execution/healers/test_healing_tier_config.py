"""Tests for healing_tier_config threshold consolidation."""
import unittest


class TestHealingTierConfigConstants(unittest.TestCase):
    """Test healing tier constants from L0 source of truth."""

    def test_healing_confidence_x_imported(self):
        """HEALING_CONFIDENCE_X must be imported from path_constants."""
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X
        self.assertEqual(HEALING_CONFIDENCE_X, 0.80)

    def test_healing_confidence_y_imported(self):
        """HEALING_CONFIDENCE_Y must be imported from path_constants."""
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y
        self.assertEqual(HEALING_CONFIDENCE_Y, 0.50)

    def test_ssot_score_det_imported(self):
        """SSOT_SCORE_THRESHOLD_DET must be imported from path_constants."""
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_DET
        self.assertEqual(SSOT_SCORE_THRESHOLD_DET, 13)

    def test_ssot_score_qwen_imported(self):
        """SSOT_SCORE_THRESHOLD_QWEN must be imported from path_constants."""
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_QWEN
        self.assertEqual(SSOT_SCORE_THRESHOLD_QWEN, 26)

    def test_qwen_14b_model_id_imported(self):
        """QWEN_14B_MODEL_ID must be imported from path_constants."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID
        self.assertEqual(QWEN_14B_MODEL_ID, "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4")


class TestHealingTierConfigClass(unittest.TestCase):
    """Test HealingTierConfig dataclass."""

    def test_config_creation(self):
        """HealingTierConfig must be creatable with required fields."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
            QWEN_14B_MODEL_ID,
            HealingTierConfig,
        )
        config = HealingTierConfig(
            heal_confidence_x=HEALING_CONFIDENCE_X,
            heal_confidence_y=HEALING_CONFIDENCE_Y,
            max_heal_retries=3,
            model_qwen_vllm_id="test-qwen-7b",
            model_qwen_14b_vllm_id=QWEN_14B_MODEL_ID,
            model_gemini_2_5_pro_id="gemini-2.5-pro",
            enable_bmg_embeddings=True,
        )
        self.assertEqual(config.heal_confidence_x, 0.80)
        self.assertEqual(config.heal_confidence_y, 0.50)
        self.assertEqual(config.max_heal_retries, 3)

    def test_load_default_config(self):
        """load_default_healing_tier_config must return valid config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HealingTierConfig,
            load_default_healing_tier_config,
        )
        config = load_default_healing_tier_config()
        self.assertIsInstance(config, HealingTierConfig)
        self.assertEqual(config.heal_confidence_x, 0.80)
        self.assertEqual(config.heal_confidence_y, 0.50)


class TestHealingTierConfigAll(unittest.TestCase):
    """Test __all__ exports."""

    def test_all_exports_thresholds(self):
        """__all__ must export healing threshold constants."""
        from agentic_core.L2_execution.healers import healing_tier_config
        self.assertIn("HEALING_CONFIDENCE_X", healing_tier_config.__all__)
        self.assertIn("HEALING_CONFIDENCE_Y", healing_tier_config.__all__)
        self.assertIn("SSOT_SCORE_THRESHOLD_DET", healing_tier_config.__all__)
        self.assertIn("SSOT_SCORE_THRESHOLD_QWEN", healing_tier_config.__all__)
        self.assertIn("QWEN_14B_MODEL_ID", healing_tier_config.__all__)
        self.assertIn("HealingTierConfig", healing_tier_config.__all__)
        self.assertIn("load_default_healing_tier_config", healing_tier_config.__all__)


if __name__ == '__main__':
    unittest.main()
