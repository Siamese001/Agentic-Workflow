#!/usr/bin/env python3
"""
Tests for base class enforcement best practices.

Best Practice: Each agent in L0-L5 layer directories should inherit from 
its canonical layer base class (L0Agent, L1Agent, etc.).
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestBaseClassEnforcement(unittest.TestCase):
    """Test base class enforcement patterns."""
    
    @classmethod
    def setUpClass(cls):
        """Load agent discovery data once."""
        import json
        discovery_path = project_root / "agent_discovery_full.json"
        if discovery_path.exists():
            cls.agents = json.loads(discovery_path.read_text(encoding='utf-8'))
        else:
            cls.agents = []
        
        cls.LAYER_BASES = {
            'L0': 'L0Agent',
            'L1': 'L1Agent',
            'L2': 'L2Agent',
            'L3': 'L3Agent',
            'L4': 'L4Agent',
            'L5': 'L5Agent',
        }
    
    def test_01_layer_bases_exist(self):
        """Test that all layer base classes exist and are importable."""
        try:
            from agentic_core.bases import L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent
            
            # Verify each has expected attributes
            for base in [L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent]:
                self.assertTrue(hasattr(base, 'name'), f"{base.__name__} missing 'name' attribute")
                self.assertTrue(hasattr(base, 'layer'), f"{base.__name__} missing 'layer' attribute")
        except ImportError as e:
            self.fail(f"Failed to import layer bases: {e}")
    
    def test_02_layer_bases_have_healer_mixin(self):
        """Test that all layer bases include HealerMixin."""
        from agentic_core.bases import L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent
        
        for base in [L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent]:
            # Check MRO includes HealerMixin
            mro_names = [c.__name__ for c in base.__mro__]
            self.assertIn('HealerMixin', mro_names, 
                         f"{base.__name__} should inherit from HealerMixin")
    
    def test_03_layer_bases_have_mcp_hardened_mixin(self):
        """Test that all layer bases include MCPHardenedMixin."""
        from agentic_core.bases import L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent
        
        for base in [L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent]:
            # Check MRO includes MCPHardenedMixin
            mro_names = [c.__name__ for c in base.__mro__]
            self.assertIn('MCPHardenedMixin', mro_names, 
                         f"{base.__name__} should inherit from MCPHardenedMixin")
    
    def test_04_base_class_enforcer_agent_exists(self):
        """Test that BaseClassEnforcerAgent exists and is functional."""
        try:
            from agentic_core.L5_safety.validators.BaseClassEnforcerAgent import (
                BaseClassEnforcerAgent, get_base_class_enforcer
            )
            
            enforcer = get_base_class_enforcer(project_root)
            self.assertIsNotNone(enforcer)
            self.assertEqual(enforcer.name, "BaseClassEnforcerAgent")
            self.assertEqual(enforcer.layer, "L5")
        except ImportError as e:
            self.fail(f"Failed to import BaseClassEnforcerAgent: {e}")
    
    def test_05_base_class_enforcer_can_scan(self):
        """Test that BaseClassEnforcerAgent can scan for violations."""
        from agentic_core.L5_safety.validators.BaseClassEnforcerAgent import get_base_class_enforcer
        
        enforcer = get_base_class_enforcer(project_root)
        result = enforcer.scan_violations()
        
        # Should return expected structure
        self.assertIn('total_layer_agents', result)
        self.assertIn('compliant_count', result)
        self.assertIn('violation_count', result)
        self.assertIn('compliance_rate', result)
        self.assertIn('violations', result)
        
        # Counts should be non-negative
        self.assertGreaterEqual(result['total_layer_agents'], 0)
        self.assertGreaterEqual(result['compliant_count'], 0)
        self.assertGreaterEqual(result['violation_count'], 0)
    
    def test_06_base_class_enforcer_inherits_from_l5agent(self):
        """Test that BaseClassEnforcerAgent itself uses correct layer base."""
        from agentic_core.L5_safety.validators.BaseClassEnforcerAgent import BaseClassEnforcerAgent
        from agentic_core.bases import L5Agent
        
        # Check MRO
        mro_names = [c.__name__ for c in BaseClassEnforcerAgent.__mro__]
        self.assertIn('L5Agent', mro_names, 
                     "BaseClassEnforcerAgent should inherit from L5Agent")
    
    def test_07_layer_agents_have_layer_attribute(self):
        """Test that discovered layer agents have 'layer' attribute in discovery."""
        if not self.agents:
            self.skipTest("No agent discovery data available")
        
        layer_agents = [a for a in self.agents if a.get('layer') in self.LAYER_BASES]
        self.assertGreater(len(layer_agents), 0, "Should have layer agents in discovery")
        
        for agent in layer_agents[:10]:  # Sample check
            self.assertIn('layer', agent)
            self.assertIn(agent['layer'], self.LAYER_BASES)


class TestLayerBaseConsistency(unittest.TestCase):
    """Test consistency across layer base classes."""
    
    def test_01_all_bases_have_heal_repository(self):
        """Test that all layer bases have heal_repository method."""
        from agentic_core.bases import L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent
        
        for base in [L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent]:
            self.assertTrue(hasattr(base, 'heal_repository'),
                           f"{base.__name__} should have heal_repository method")
    
    def test_02_all_bases_have_run_self_tests(self):
        """Test that all layer bases have _run_self_tests method."""
        from agentic_core.bases import L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent
        
        for base in [L0Agent, L1Agent, L2Agent, L3Agent, L4Agent, L5Agent]:
            # L0Agent uses delegation, others use self-tests
            has_tests = hasattr(base, '_run_self_tests') or hasattr(base, '_delegate_tests')
            self.assertTrue(has_tests,
                           f"{base.__name__} should have _run_self_tests or _delegate_tests method")
    
    def test_03_bases_export_from_init(self):
        """Test that bases are properly exported from __init__.py."""
        from agentic_core.bases import __all__
        
        expected = ['L0Agent', 'L1Agent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent']
        for base_name in expected:
            self.assertIn(base_name, __all__, f"{base_name} should be in __all__")


if __name__ == '__main__':
    unittest.main()
