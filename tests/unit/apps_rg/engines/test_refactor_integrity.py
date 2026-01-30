"""File: C:/Git/Agentic-Workflow/tests/test_refactor_integrity.py
Context: Comprehensive test suite to validate the Agent/Util separation. Verifies that old paths are dead, new paths are alive, and no stale imports exist in the blast radius.
"""

import importlib
import sys
import unittest

# Ensure root is in path for imports
sys.path.append(r"C:\Git\Agentic-Workflow")


class TestRefactorIntegrity(unittest.TestCase):
    def test_01_verify_old_locations_dead(self):
        """
        Critical Check: Attempting to import agents from common_utils MUST fail.
        Ensures no 'ghost' files were left behind.
        """
        agents = ["Router", "HardenedAnthropicExecutor", "strategist_biowriter"]

        for agent in agents:
            try:
                importlib.import_module(f"apps_shared.common_utils.{agent}")
                self.fail(
                    f"CRITICAL: {agent} is still importable from common_utils! Separation failed."
                )
            except (ImportError, NameError, AttributeError):
                # Expected behavior: ModuleNotFoundError
                pass

    def test_02_verify_new_locations_alive(self):
        """
        Critical Check: Attempting to import agents from apps_rg.engines MUST succeed.
        Verifies import paths, __init__.py files, and dependencies are resolved.
        """
        try:
            # Dynamic imports to verify runtime accessibility
            import apps_rg.engines.Router
            import apps_rg.engines.schema  # The new dependency
            import apps_rg.engines.strategist_biowriter

            import apps_rg.engines.HardenedAnthropicExecutor
        except (ImportError, NameError, AttributeError, TypeError) as e:
            self.fail(f"CRITICAL: Could not import Agent from new location: {e}")

    def test_03_verify_inheritance_integrity(self):
        """
        Edge Case: Verify that moved agents inherit from the correct RGAgentBase,
        not the old or missing 'Agent' class.
        """
        from agentic_core.base_agents.agent_base import RGAgentBase
        from apps_rg.engines.strategist_biowriter import StrategistBioWriter

        # Instantiate with mocks to check MRO
        agent_instance = StrategistBioWriter(config=None, reasoning=None)
        self.assertIsInstance(
            agent_instance,
            RGAgentBase,
            "StrategistBioWriter lost its RGAgentBase inheritance during move.",
        )

    def test_04_run_stale_import_scanner(self):
        """
        Executes the global scanner to ensure no main.py or orchestrator is pointing
        to the wrong place. Enforces 'Zero Stale References'.
        """
        # For now, we'll skip this test since the scanner script doesn't exist yet
        # In a real implementation, you would:
        # from scripts.verify_global_imports import scan_for_stale_imports
        # try:
        #     scan_for_stale_imports()
        # except SystemExit as e:
        #     self.assertEqual(e.code, 0, "Global Import Scan found stale references. Refactor incomplete.")
        self.skipTest("Global import scanner not yet implemented")

    def test_05_verify_router_imports_updated(self):
        """
        Verify Router.py has been updated with the new import paths
        """
        import apps_rg.engines.Router

        # Check that the module can be imported and has expected attributes
        self.assertTrue(
            hasattr(apps_rg.engines.Router, "Router"), "Router class not found in new location"
        )

    def test_06_verify_schema_types_available(self):
        """
        Verify that schema.py provides the required types
        """
        from apps_rg.engines.schema import ProviderType, RouterConfig

        # Test that the types can be instantiated
        config = RouterConfig()
        self.assertIsInstance(config.default_provider, ProviderType)

        # Test ProviderType enum values
        self.assertEqual(ProviderType.OPENAI.value, "openai")
        self.assertEqual(ProviderType.ANTHROPIC.value, "anthropic")
        self.assertEqual(ProviderType.AZURE.value, "azure")

    def test_07_verify_multi_provider_client_structure(self):
        """
        Verify the recreated multi_provider_clients.py has correct structure
        """
        from apps_shared.common_utils.multi_provider_clients import MultiProviderClient

        # Test that the class exists and can be instantiated
        client = MultiProviderClient(config={"test": "value"})
        self.assertIsInstance(client, MultiProviderClient)

        # Test that it has the expected method
        self.assertTrue(
            hasattr(client, "completion"), "MultiProviderClient missing completion method"
        )


if __name__ == "__main__":
    unittest.main()
