import os
import sys
import unittest
from dataclasses import is_dataclass

# Add the workspace root to Python path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Now import with absolute paths
from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent
from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent


class TestAgentHardening(unittest.TestCase):
    """
    MANDATORY: 100% Pass Required.
    Targets MRO Stability, Config Injection, and Sovereign Sealing (Immutability).
    """

    def test_mro_root_injection(self):
        """
        Edge Case: Verify LICAgentBase is strictly the first parent.
        """
        hop1_mro = HOP1ProfileAnalysisAgent.mro()
        hop2_mro = HOP2ResearchAgent.mro()

        # Verify MRO structure: Concrete -> Mixin -> LICAgentBase -> ...
        self.assertEqual(
            hop1_mro[1].__name__,
            "LICAgentBase",
            "HOP1 MRO Violation: LICAgentBase must be second in MRO",
        )
        self.assertEqual(
            hop2_mro[1].__name__,
            "LICAgentBase",
            "HOP2 MRO Violation: LICAgentBase must be second in MRO",
        )

        # Verify SubatomicTestingMixin is present
        self.assertIn("SubatomicTestingMixin", [cls.__name__ for cls in hop1_mro])
        self.assertIn("SubatomicTestingMixin", [cls.__name__ for cls in hop2_mro])

        print("SUCCESS: Root Injection Pattern verified.")

    def test_sovereign_seal_immutability(self):
        """
        Edge Case: Ensure 'Sovereign Seal' prevents state drift at runtime.
        Replacing 'frozen=True' check with behavioral check.
        """
        agent = HOP1ProfileAnalysisAgent()

        # Verify initial attributes are accessible
        self.assertTrue(hasattr(agent, "config"), "Config should be present")
        self.assertTrue(hasattr(agent, "_sealed"), "Seal flag should be present")
        self.assertTrue(agent._sealed, "Seal should be engaged after initialization")

        # Verify router was set before sealing
        self.assertTrue(hasattr(agent, "router"), "Router should be set before sealing")

        # Attempt illegal mutation - should fail
        with self.assertRaises(AttributeError) as cm:
            agent.new_variable = "mutation_attempt"

        self.assertIn("Sovereign Seal Active", str(cm.exception), "Seal failed to block mutation")

        # Attempt to modify existing attribute - should also fail
        with self.assertRaises(AttributeError) as cm:
            agent.config = None

        self.assertIn(
            "Sovereign Seal Active", str(cm.exception), "Seal failed to block config modification"
        )

        print("SUCCESS: Sovereign Seal Immutability enforced.")

    def test_sovereign_seal_hop2(self):
        """
        Edge Case: Test HOP2 Sovereign Seal with defensive config loading.
        """
        agent = HOP2ResearchAgent()

        # Verify seal is engaged
        self.assertTrue(hasattr(agent, "_sealed"), "Seal flag should be present")
        self.assertTrue(agent._sealed, "Seal should be engaged after initialization")

        # Verify config was loaded defensively
        self.assertTrue(hasattr(agent, "vector_params"), "Vector params should be loaded")
        self.assertTrue(hasattr(agent, "critique_params"), "Critique params should be loaded")

        # Attempt mutation after sealing
        with self.assertRaises(AttributeError) as cm:
            agent.memory_store = "hacked"

        self.assertIn(
            "Sovereign Seal Active", str(cm.exception), "HOP2 Seal failed to block mutation"
        )

        print("SUCCESS: HOP2 Sovereign Seal and defensive config loading verified.")

    def test_defensive_config_resolution(self):
        """
        Edge Case: Verify HOP2 handles the missing 'research_agent' key gracefully.
        This test verifies the RCA FIX for naming mismatch.
        """
        try:
            agent = HOP2ResearchAgent()
            # If we get here, the config was loaded successfully (either 'research_agent' or 'research' exists)
            self.assertIsNotNone(
                agent.vector_params, "Vector params should be loaded regardless of config key name"
            )

        except AttributeError as e:
            # If AttributeError is raised, it should be the handled fault with specific message
            if "Sovereign Blueprint Fault" not in str(e):
                self.fail(f"Caught generic AttributeError instead of handled fault: {e}")
            # Expected path for missing config - test passes
        except Exception as e:
            self.fail(f"Unexpected exception type: {type(e).__name__}: {e}")

        print("SUCCESS: Defensive Config Resolution active.")

    def test_dataclass_structure_preserved(self):
        """
        Verify dataclass structure is maintained with Sovereign Seal.
        """
        # Both agents should still be proper dataclasses
        self.assertTrue(is_dataclass(HOP1ProfileAnalysisAgent), "HOP1 should remain a dataclass")
        self.assertTrue(is_dataclass(HOP2ResearchAgent), "HOP2 should remain a dataclass")

        # Verify field definitions work
        hop1 = HOP1ProfileAnalysisAgent()
        hop2 = HOP2ResearchAgent()

        # Check that dataclass fields are properly initialized
        self.assertIsNone(hop2.memory_store, "Optional field should default to None")
        self.assertIsNone(hop2.search_client, "Optional field should default to None")
        self.assertIsNone(hop2.llm_client, "Optional field should default to None")

        print("SUCCESS: Dataclass structure preserved with Sovereign Seal.")

    def test_seal_timing(self):
        """
        Verify seal is engaged AFTER all initialization is complete.
        This prevents the 'premature sealing' bug.
        """
        # Test HOP1
        hop1 = HOP1ProfileAnalysisAgent()

        # Router should be set (happens before sealing)
        self.assertIsNotNone(hop1.router, "Router must be set before seal engages")

        # Seal should be engaged
        self.assertTrue(hop1._sealed, "Seal must be engaged after initialization")

        # Test HOP2
        hop2 = HOP2ResearchAgent()

        # Config params should be set (happens before sealing)
        self.assertIsNotNone(hop2.vector_params, "Vector params must be set before seal engages")
        self.assertIsNotNone(
            hop2.critique_params, "Critique params must be set before seal engages"
        )

        # Seal should be engaged
        self.assertTrue(hop2._sealed, "Seal must be engaged after initialization")

        print("SUCCESS: Seal timing verified - initialization complete before sealing.")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
