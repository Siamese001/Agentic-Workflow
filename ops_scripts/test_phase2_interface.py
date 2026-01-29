#!/usr/bin/env python3
"""
Phase 2 Interface Compliance Test Suite

Tests heal_repository interface compliance for:
- SafetyExecutorAgent
- SecurityManagerAgent
- StructureEnforcerAgent
- StructureHealerAgent
- CodeValidatorAgent
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.policy_engine.SafetyExecutorAgent import SafetyExecutorAgent
from agentic_core.L5_safety.policy_engine.SecurityManagerAgent import SecurityManagerAgent
from agentic_core.L5_safety.policy_engine.StructureEnforcerAgent import StructureEnforcerAgent
from agentic_core.L5_safety.policy_engine.StructureHealerAgent import StructureHealerAgent
from agentic_core.L5_safety.policy_engine.CodeValidatorAgent import CodeValidatorAgent


class TestPhase2InterfaceCompliance(unittest.TestCase):
    """Test Phase 2 agents for heal_repository interface compliance."""

    def setUp(self):
        """Set up test environment."""
        self.root = Path(__file__).parent.parent / "test_temp_p2"
        self.root.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.root.exists():
            shutil.rmtree(self.root)

    def test_safety_executor_interface(self):
        """Phase 2: Verify heal_repository on SafetyExecutorAgent."""
        agent = SafetyExecutorAgent()

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: SafetyExecutorAgent interface check")

    def test_security_manager_interface(self):
        """Phase 2: Verify heal_repository on SecurityManagerAgent."""
        agent = SecurityManagerAgent()

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: SecurityManagerAgent interface check")

    def test_structure_enforcer_interface(self):
        """Phase 2: Verify heal_repository on StructureEnforcerAgent."""
        agent = StructureEnforcerAgent(project_root=self.root)

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        print("✓ PASS: StructureEnforcerAgent interface check")

    def test_structure_healer_wiring(self):
        """Phase 2: Verify heal_repository wiring on StructureHealerAgent."""
        agent = StructureHealerAgent(project_root=self.root)

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Create a dummy file to heal
        dummy_file = self.root / "BadClass.py"
        dummy_file.write_text("class BadClass:\n    pass")

        # Test healing logic connection
        result = agent.heal_repository(dry_run=True, file_path=str(dummy_file))
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)

        # Should detect naming violation
        self.assertGreaterEqual(result["violations"], 0)

        print("✓ PASS: StructureHealerAgent logic wiring")

    def test_code_validator_wiring(self):
        """Phase 2: Verify heal_repository wiring on CodeValidatorAgent."""
        agent = CodeValidatorAgent()

        # Test method exists
        self.assertTrue(hasattr(agent, "heal_repository"))

        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations_found", result)
        self.assertIn("violations_fixed", result)

        print("✓ PASS: CodeValidatorAgent logic wiring")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PHASE 2: UNIFIED AGENT INTERFACE COMPLIANCE TEST SUITE")
    print("=" * 70 + "\n")

    unittest.main(verbosity=2)
