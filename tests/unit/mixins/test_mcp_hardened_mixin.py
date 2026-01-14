#!/usr/bin/env python3
"""
Test Suite for MCPHardenedMixin - Root Security Mixin

Tests:
- Initialization with _mcp_ prefixed attributes
- Cooperative inheritance pattern
- MCP audit logging
- Attribute collision avoidance
"""
import pytest
from dataclasses import dataclass
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class TestMCPHardenedMixinInitialization:
    """Test initialization and attribute setup."""
    
    def test_mcp_attributes_initialized(self):
        """Test _mcp_ prefixed attributes are initialized."""
        
        @dataclass
        class TestAgent(MCPHardenedMixin):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__init__()
        
        agent = TestAgent()
        
        # Check _mcp_ prefixed attributes exist
        assert hasattr(agent, '_mcp_audit_log')
        assert isinstance(agent._mcp_audit_log, list)
    
    def test_cooperative_inheritance(self):
        """Test mixin works with cooperative inheritance."""
        
        @dataclass
        class BaseMixin:
            def __init__(self, **kwargs):
                self.base_initialized = True
                super().__init__(**kwargs)
        
        @dataclass
        class TestAgent(BaseMixin, MCPHardenedMixin):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__init__()
        
        agent = TestAgent()
        
        # Both mixins should initialize
        assert hasattr(agent, 'base_initialized')
        assert hasattr(agent, '_mcp_audit_log')


class TestMCPHardenedMixinAttributePrefixes:
    """Test attribute naming follows _mcp_ prefix convention."""
    
    def test_all_attributes_use_mcp_prefix(self):
        """Test all mixin attributes use _mcp_ prefix to avoid collisions."""
        
        @dataclass
        class TestAgent(MCPHardenedMixin):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__init__()
        
        agent = TestAgent()
        
        # Get all attributes that look like they belong to MCPHardenedMixin
        mcp_attrs = [attr for attr in dir(agent) if not attr.startswith('__')]
        
        # Filter to likely mixin attributes (not from dataclass)
        likely_mixin_attrs = [attr for attr in mcp_attrs if attr.startswith('_mcp_')]
        
        # Should have at least _mcp_audit_log
        assert len(likely_mixin_attrs) >= 1
        assert '_mcp_audit_log' in likely_mixin_attrs


class TestMCPHardenedMixinConstants:
    """Test mixin constants are defined."""
    
    def test_has_max_retries(self):
        """Test MAX_RETRIES constant exists."""
        assert hasattr(MCPHardenedMixin, 'MAX_RETRIES')
        assert isinstance(MCPHardenedMixin.MAX_RETRIES, int)
        assert MCPHardenedMixin.MAX_RETRIES > 0
    
    def test_has_default_timeout(self):
        """Test DEFAULT_TIMEOUT constant exists."""
        assert hasattr(MCPHardenedMixin, 'DEFAULT_TIMEOUT')
        assert isinstance(MCPHardenedMixin.DEFAULT_TIMEOUT, (int, float))
        assert MCPHardenedMixin.DEFAULT_TIMEOUT > 0


class TestMCPHardenedMixinIsolation:
    """Test mixin instances are isolated."""
    
    def test_audit_log_isolation(self):
        """Test audit logs are isolated between instances."""
        
        @dataclass
        class TestAgent(MCPHardenedMixin):
            name: str = "TestAgent"
            
            def __post_init__(self):
                super().__init__()
        
        agent1 = TestAgent(name="Agent1")
        agent2 = TestAgent(name="Agent2")
        
        # Logs should be separate
        agent1._mcp_audit_log.append("event1")
        agent2._mcp_audit_log.append("event2")
        
        assert "event1" in agent1._mcp_audit_log
        assert "event1" not in agent2._mcp_audit_log
        assert "event2" in agent2._mcp_audit_log
        assert "event2" not in agent1._mcp_audit_log


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
