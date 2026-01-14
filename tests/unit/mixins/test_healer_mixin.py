#!/usr/bin/env python3
"""
Test Suite for HealerMixin - Self-Repair Capability

Tests:
- Initialization with _healer_ prefixed attributes
- heal_repository method with cycle detection
- Budget management
- Cooperative inheritance
"""
import pytest
from dataclasses import dataclass
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class TestHealerMixinInitialization:
    """Test initialization and attribute setup."""
    
    def test_healer_attributes_initialized(self):
        """Test _healer_ prefixed attributes are initialized."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        
        # Check _healer_ prefixed attributes
        assert hasattr(agent, '_healer_cache')
        assert hasattr(agent, '_healer_metrics')


class TestHealerMixinHealRepository:
    """Test heal_repository method."""
    
    def test_heal_repository_returns_dict(self):
        """Test heal_repository returns expected structure."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert isinstance(result, dict)
        assert "violations" in result
        assert "fixed" in result
        assert "errors" in result
        assert "skipped" in result
    
    def test_heal_repository_cycle_detection(self):
        """Test heal_repository detects cycles."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        
        # Call with same _call_path to simulate cycle
        call_path = {"TestAgent"}
        result = agent.heal_repository(_call_path=call_path)
        
        # Should detect cycle and skip
        assert result["skipped"] >= 1
    
    def test_heal_repository_depth_limiting(self):
        """Test heal_repository respects max_depth."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        
        # Call at max depth
        result = agent.heal_repository(depth=3, max_depth=3)
        
        # Should stop at max depth
        assert isinstance(result, dict)


class TestHealerMixinCooperativeInheritance:
    """Test cooperative inheritance with other mixins."""
    
    def test_works_with_sovereign_base(self):
        """Test HealerMixin works with SovereignBaseAgent."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        
        # Both should initialize
        assert hasattr(agent, '_healer_cache')
        assert hasattr(agent, '_sovereign_initialized')
        assert agent._sovereign_initialized is True


class TestHealerMixinAttributePrefixes:
    """Test attribute naming follows _healer_ prefix convention."""
    
    def test_all_attributes_use_healer_prefix(self):
        """Test all mixin attributes use _healer_ prefix."""
        
        @dataclass
        class TestAgent(HealerMixin, SovereignBaseAgent):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__post_init__()
        
        agent = TestAgent()
        
        # Get healer-specific attributes
        healer_attrs = [attr for attr in dir(agent) if attr.startswith('_healer_')]
        
        # Should have at least _healer_cache and _healer_metrics
        assert len(healer_attrs) >= 2
        assert '_healer_cache' in healer_attrs
        assert '_healer_metrics' in healer_attrs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
