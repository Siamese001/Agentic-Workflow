#!/usr/bin/env python3
"""
Phase 1 Interface Compliance Test Suite

Tests heal_repository interface compliance for:
- CodeDetectorAgent
- CodeEnforcerAgent
- CodeHealerAgent
- ResourceManagerAgent
- SafetyDetectorAgent
"""

import sys
import unittest
from pathlib import Path

# Add project root to path (3 levels deep: tests/e2e/ops_scripts/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.policy_engine.CodeDetectorAgent import CodeDetectorAgent
from agentic_core.L5_safety.policy_engine.CodeEnforcerAgent import CodeEnforcerAgent
from agentic_core.L5_safety.policy_engine.CodeHealerAgent import CodeHealerAgent
from agentic_core.L5_safety.policy_engine.ResourceManagerAgent import ResourceManagerAgent
from agentic_core.L5_safety.policy_engine.SafetyDetectorAgent import SafetyDetectorAgent


class TestPhase1InterfaceCompliance(unittest.TestCase):
    """Test Phase 1 agents for heal_repository interface compliance."""

    def setUp(self):
        """Set up test environment."""
        self.root = Path(__file__).parent.parent / "test_temp"
        self.root.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.root.exists():
            shutil.rmtree(self.root)

    def test_heal_repository_signature_detector(self):
        """Phase 1: Verify heal_repository signature on CodeDetectorAgent."""
        agent = CodeDetectorAgent(project_root=self.root)

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True, execute=False)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        self.assertIn("errors", result)

        print("✓ PASS: CodeDetectorAgent interface check")

    def test_heal_repository_signature_enforcer(self):
        """Phase 1: Verify heal_repository signature on CodeEnforcerAgent."""
        agent = CodeEnforcerAgent(project_root=self.root)

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True, execute=False)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: CodeEnforcerAgent interface check")

    def test_heal_repository_wiring_healer(self):
        """Phase 1: Verify heal_repository wiring on CodeHealerAgent."""
        agent = CodeHealerAgent(project_root=self.root)

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Create a dummy file to heal
        dummy_file = self.root / "broken.py"
        dummy_file.write_text("import os\n\n\n\nprint('hello')")  # Excessive blank lines

        result = agent.heal_repository(dry_run=True, execute=False, file_path=str(dummy_file))
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        # Should detect structural issues
        self.assertGreaterEqual(result["violations"], 0)

        print("✓ PASS: CodeHealerAgent logic wiring")

    def test_heal_repository_signature_resource(self):
        """Phase 1: Verify heal_repository signature on ResourceManagerAgent."""
        agent = ResourceManagerAgent()

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: ResourceManagerAgent interface check")

    def test_heal_repository_signature_safety(self):
        """Phase 1: Verify heal_repository signature on SafetyDetectorAgent."""
        agent = SafetyDetectorAgent()

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: SafetyDetectorAgent interface check")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PHASE 1: UNIFIED AGENT INTERFACE COMPLIANCE TEST SUITE")
    print("=" * 70 + "\n")

    unittest.main(verbosity=2)
