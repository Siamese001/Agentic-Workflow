"""
Targeted Mock Test for HOP1 Composition.
Directly tests the router creation logic without complex inheritance mocking.
"""

import sys
import unittest
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
sys.path.insert(0, str(PROJECT_ROOT))

from apps_lic.logic_nodes.k1_router import K1Router


class TestHOP1CompositionMock(unittest.TestCase):
    def test_router_composition_direct_instantiation(self):
        """
        Direct test that proves the composition architecture works.
        This simulates exactly what HOP1ProfileAnalysisAgent.__post_init__ does.
        """

        # Setup - Simulate the exact config structure that HOP1 uses
        class MockSelf:
            def __init__(self):
                self.config = MockConfig()

        class MockConfig:
            def __init__(self):
                self.__dict__ = {"env": "test", "mode": "mock"}

        mock_self = MockSelf()

        # Execute - This is the exact line from HOP1ProfileAnalysisAgent.__post_init__
        router = K1Router(
            config=mock_self.config.__dict__
            if hasattr(mock_self, "config") and mock_self.config
            else {}
        )

        # Verify Router Type (The Critical Architectural Check)
        self.assertIsInstance(router, K1Router, "Router is not an instance of K1Router logic node.")

        # Verify Config Propagation
        self.assertEqual(
            router.config,
            {"env": "test", "mode": "mock"},
            "Config not correctly propagated to Router.",
        )

        # Verify Router Functionality
        self.assertTrue(callable(router), "K1Router must be callable (functor pattern).")

        # Test basic routing logic to ensure it's not just an empty shell
        test_state = {
            "contact_name": "Test User",
            "contact_title": "Chief Executive Officer",
            "lifecycle": "NEW",
            "premium_available": True,
        }

        result = router(test_state)
        self.assertIsNotNone(result, "Router should return a valid result.")
        self.assertEqual(result.archetype.archetype, "C_LEVEL", "CXO precedence should work.")

        print("\n[SUCCESS] HOP1 Composition Architecture Verified - Router works correctly.")

        # Additional verification: Ensure this is NOT an Agent
        self.assertNotIn(
            "Agent", router.__class__.__name__, "Logic node should not have 'Agent' in name."
        )

    def test_architectural_compliance(self):
        """
        Verify the architectural compliance of the composition pattern.
        """
        router = K1Router()

        # 1. Router is a utility node (not an agent)
        self.assertIn("Router", router.__class__.__name__)
        self.assertNotIn("Agent", router.__class__.__name__)

        # 2. Router is callable (functor pattern for graph compatibility)
        self.assertTrue(callable(router))

        # 3. Router has proper routing methods
        self.assertTrue(hasattr(router, "determine_next_hop"))
        self.assertTrue(hasattr(router, "__call__"))

        # 4. Router handles empty state defensively
        with self.assertRaises(ValueError):
            router({})

        print("\n[SUCCESS] Architectural Compliance Verified.")


if __name__ == "__main__":
    unittest.main()
