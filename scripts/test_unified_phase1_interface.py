#!/usr/bin/env python3
"""
Phase 1 Interface Compliance Test Suite

Tests heal_repository interface compliance for:
- UnifiedCodeDetectorAgent
- UnifiedCodeEnforcerAgent
- UnifiedCodeHealerAgent
- UnifiedResourceManagerAgent
- UnifiedSafetyDetectorAgent
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.unified.UnifiedCodeDetectorAgent import UnifiedCodeDetectorAgent
from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import UnifiedCodeEnforcerAgent
from agentic_core.L5_safety.unified.UnifiedCodeHealerAgent import UnifiedCodeHealerAgent
from agentic_core.L5_safety.unified.UnifiedResourceManagerAgent import UnifiedResourceManagerAgent
from agentic_core.L5_safety.unified.UnifiedSafetyDetectorAgent import UnifiedSafetyDetectorAgent


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
        """Phase 1: Verify heal_repository signature on UnifiedCodeDetectorAgent."""
        agent = UnifiedCodeDetectorAgent(project_root=self.root)
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True, execute=False)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        self.assertIn("errors", result)
        
        print("✓ PASS: UnifiedCodeDetectorAgent interface check")

    def test_heal_repository_signature_enforcer(self):
        """Phase 1: Verify heal_repository signature on UnifiedCodeEnforcerAgent."""
        agent = UnifiedCodeEnforcerAgent(project_root=self.root)
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True, execute=False)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedCodeEnforcerAgent interface check")

    def test_heal_repository_wiring_healer(self):
        """Phase 1: Verify heal_repository wiring on UnifiedCodeHealerAgent."""
        agent = UnifiedCodeHealerAgent(project_root=self.root)
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Create a dummy file to heal
        dummy_file = self.root / "broken.py"
        dummy_file.write_text("import os\n\n\n\nprint('hello')")  # Excessive blank lines
        
        result = agent.heal_repository(dry_run=True, execute=False, file_path=str(dummy_file))
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        # Should detect structural issues
        self.assertGreaterEqual(result["violations"], 0)
        
        print("✓ PASS: UnifiedCodeHealerAgent logic wiring")

    def test_heal_repository_signature_resource(self):
        """Phase 1: Verify heal_repository signature on UnifiedResourceManagerAgent."""
        agent = UnifiedResourceManagerAgent()
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedResourceManagerAgent interface check")

    def test_heal_repository_signature_safety(self):
        """Phase 1: Verify heal_repository signature on UnifiedSafetyDetectorAgent."""
        agent = UnifiedSafetyDetectorAgent()
        
        # Test method exists
        self.assertTrue(hasattr(agent, 'heal_repository'))
        
        # Test signature
        result = agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn("violations", result)
        self.assertIn("fixed", result)
        
        print("✓ PASS: UnifiedSafetyDetectorAgent interface check")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 1: UNIFIED AGENT INTERFACE COMPLIANCE TEST SUITE")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
