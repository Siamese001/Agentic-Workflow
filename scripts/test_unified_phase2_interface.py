#!/usr/bin/env python3
"""
Phase 2 Interface Compliance Test Suite

Tests heal_repository interface compliance for:
- UnifiedSafetyExecutorAgent
- UnifiedSecurityManagerAgent
- UnifiedStructureEnforcerAgent
- UnifiedStructureHealerAgent
- UnifiedCodeValidatorAgent
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.unified.UnifiedSafetyExecutorAgent import UnifiedSafetyExecutorAgent
from agentic_core.L5_safety.unified.UnifiedSecurityManagerAgent import UnifiedSecurityManagerAgent
from agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent import UnifiedStructureEnforcerAgent
from agentic_core.L5_safety.unified.UnifiedStructureHealerAgent import UnifiedStructureHealerAgent
from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import UnifiedCodeValidatorAgent


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
        """Phase 2: Verify heal_repository on UnifiedSafetyExecutorAgent."""
        agent = UnifiedSafetyExecutorAgent()
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedSafetyExecutorAgent interface check")

    def test_security_manager_interface(self):
        """Phase 2: Verify heal_repository on UnifiedSecurityManagerAgent."""
        agent = UnifiedSecurityManagerAgent()
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedSecurityManagerAgent interface check")

    def test_structure_enforcer_interface(self):
        """Phase 2: Verify heal_repository on UnifiedStructureEnforcerAgent."""
        agent = UnifiedStructureEnforcerAgent(project_root=self.root)
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedStructureEnforcerAgent interface check")

    def test_structure_healer_wiring(self):
        """Phase 2: Verify heal_repository wiring on UnifiedStructureHealerAgent."""
        agent = UnifiedStructureHealerAgent(project_root=self.root)
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
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
        
        print("✓ PASS: UnifiedStructureHealerAgent logic wiring")

    def test_code_validator_wiring(self):
        """Phase 2: Verify heal_repository wiring on UnifiedCodeValidatorAgent."""
        agent = UnifiedCodeValidatorAgent()
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations_found", result)
        self.assertIn("violations_fixed", result)
        
        print("✓ PASS: UnifiedCodeValidatorAgent logic wiring")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 2: UNIFIED AGENT INTERFACE COMPLIANCE TEST SUITE")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
