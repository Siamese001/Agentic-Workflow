import os
import sys
import unittest


class FinalSystemIntegrityTest(unittest.TestCase):
    """
    Final system verification of the post-migration state.
    Target: 100% Pass mandatory to close mission.
    """

    def test_legacy_void_compliance(self):
        """Case 1: Confirm the legacy_archive directory is physically gone."""
        legacy_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps_lic", "legacy_archive")
        self.assertFalse(
            os.path.exists(legacy_path),
            "CRITICAL: Legacy Data Leak detected. Archive still exists.",
        )

    def test_ssot_engines_resolution(self):
        """Case 2: Confirm agents are resolvable in the 'engines' subfolder."""
        try:
            from apps_lic.engines.CompetitorReconAgent import CompetitorReconAgent
            from apps_lic.engines.StackModernizationAgent import StackModernizationAgent

            recon = CompetitorReconAgent()
            stack = StackModernizationAgent()

            self.assertIsNotNone(
                recon, "CompetitorReconAgent failed to instantiate from engines/"
            )
            self.assertIsNotNone(
                stack, "StackModernizationAgent failed to instantiate from engines/"
            )
        except ImportError as exc:
            self.fail(f"SSOT Resolution Failure: {exc}")

    def test_logic_persistence(self):
        """Case 3: Verify the extracted logic (BioTech) is active in the new location."""
        from apps_lic.engines.CompetitorReconAgent import MockIntelProvider

        provider = MockIntelProvider()
        competitors = provider.get_competitors("X", "biotech")
        self.assertIn(
            "Ginkgo Bioworks",
            competitors,
            "LOGIC LOSS: Extracted BioTech data missing from engines/ agent.",
        )


if __name__ == "__main__":
    unittest.main()
