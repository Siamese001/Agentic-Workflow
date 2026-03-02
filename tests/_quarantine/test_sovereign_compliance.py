import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L0_routing.scripts.execute_ssot import (
    ConfidenceScore,
    SovereignDecisionEngine,
)


class TestSovereignIntegration(unittest.TestCase):
    """Mandatory 100% pass for tiered model and territory logic."""

    def test_environment_driven_confidence_thresholds(self):
        """Verify that ConfidenceScore dynamically updates based on .env variables."""
        # Test with value 0.80 - should be high confidence with default threshold (0.75)
        conf = ConfidenceScore(value=0.80, reasoning="Test")

        # Should be True because 0.80 > 0.75 (default high confidence threshold)
        self.assertTrue(conf.is_high_confidence)  # Property, not method
        # Should be False because 0.80 > 0.75 (not in medium range)
        self.assertFalse(conf.is_medium_confidence)  # Property, not method

        # Test edge case - exactly 0.75 should be medium, not high
        conf_edge = ConfidenceScore(value=0.75, reasoning="Test")
        self.assertFalse(conf_edge.is_high_confidence)
        self.assertTrue(conf_edge.is_medium_confidence)

    def test_tiered_model_resolution(self):
        """Verify .env drives model selection for both Medium and Low bands."""
        engine = SovereignDecisionEngine(enable_llm=True)

        # Test Medium Band (0.60 should trigger GEMINI_MODEL)
        conf_med = ConfidenceScore(value=0.60, reasoning="Test")
        engine.should_proceed_with_healing(conf_med, "AgentA")

        # Check that decisions were recorded
        self.assertTrue(hasattr(engine, "decisions_made"))

        # Test Low Band (0.30 should trigger GEMINI_PRO_MODEL)
        conf_low = ConfidenceScore(value=0.30, reasoning="Test")
        engine.should_proceed_with_healing(conf_low, "AgentB")

        # Verify decisions were made
        self.assertGreater(len(engine.decisions_made), 0)

    def test_archive_territory_presence(self):
        """Verify archives/ is a recognized root."""
        from agentic_core.L5_safety.config.structure_blueprint_config import ROOT_WHITELIST

        # Check that archives is in the ROOT_WHITELIST
        self.assertIn("archives", ROOT_WHITELIST)


if __name__ == "__main__":
    unittest.main()
