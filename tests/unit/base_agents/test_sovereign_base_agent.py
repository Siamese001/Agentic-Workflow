#!/usr/bin/env python3
"""
Test Suite for SovereignBaseAgent - Root of L0-L6 Architecture

Tests:
- Initialization and state management
- MRO propagation with _sovereign_initialized sentinel
- Cooperative inheritance with MCPHardenedMixin
- Core methods (execute, get_state, set_state, etc.)
- heal_repository termination point
"""
import pytest
from dataclasses import dataclass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class TestSovereignBaseAgentInitialization:
    """Test initialization and state management."""
    
    def test_default_initialization(self):
        """Test agent initializes with default values."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        assert agent.name == "TestAgent"
        assert hasattr(agent, '_config')
        assert hasattr(agent, '_state')
        assert hasattr(agent, '_authority_level')
        assert agent._authority_level == 'standard'
    
    def test_mro_sentinel_set(self):
        """Test _sovereign_initialized sentinel is set for MRO auditing."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        assert hasattr(agent, '_sovereign_initialized')
        assert agent._sovereign_initialized is True
    
    def test_custom_name(self):
        """Test agent accepts custom name."""
        agent = SovereignBaseAgent(name="CustomAgent")
        
        assert agent.name == "CustomAgent"


class TestSovereignBaseAgentStateManagement:
    """Test state management methods."""
    
    def test_set_and_get_state(self):
        """Test setting and getting state values."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        agent.set_state("key1", "value1")
        agent.set_state("key2", 42)
        
        assert agent.get_state("key1") == "value1"
        assert agent.get_state("key2") == 42
    
    def test_get_nonexistent_state(self):
        """Test getting nonexistent state returns None."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        assert agent.get_state("nonexistent") is None
    
    def test_state_isolation(self):
        """Test state is isolated between instances."""
        agent1 = SovereignBaseAgent(name="Agent1")
        agent2 = SovereignBaseAgent(name="Agent2")
        
        agent1.set_state("key", "value1")
        agent2.set_state("key", "value2")
        
        assert agent1.get_state("key") == "value1"
        assert agent2.get_state("key") == "value2"


class TestSovereignBaseAgentAuthority:
    """Test authority level management."""
    
    def test_default_authority_level(self):
        """Test default authority level is 'standard'."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        assert agent.get_authority_level() == 'standard'
    
    def test_elevate_authority(self):
        """Test authority can be elevated."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        agent.elevate_authority('elevated')
        assert agent.get_authority_level() == 'elevated'
        
        agent.elevate_authority('admin')
        assert agent.get_authority_level() == 'admin'


class TestSovereignBaseAgentLogging:
    """Test logging methods."""
    
    def test_log_info(self):
        """Test log_info doesn't raise errors."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        # Should not raise
        agent.log_info("Test info message")
    
    def test_log_warning(self):
        """Test log_warning doesn't raise errors."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        # Should not raise
        agent.log_warning("Test warning message")
    
    def test_log_error(self):
        """Test log_error doesn't raise errors."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        # Should not raise
        agent.log_error("Test error message")
    
    def test_log_feedback(self):
        """Test log_feedback doesn't raise errors."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        # Should not raise
        agent.log_feedback("workflow_123", "action_test", "success", {"detail": "test"})


class TestSovereignBaseAgentHealRepository:
    """Test heal_repository method (ROOT termination point)."""
    
    def test_heal_repository_returns_dict(self):
        """Test heal_repository returns expected dict structure."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        result = agent.heal_repository()
        
        assert isinstance(result, dict)
        assert "violations" in result
        assert "fixed" in result
        assert "errors" in result
        assert "skipped" in result
    
    def test_heal_repository_dry_run(self):
        """Test heal_repository with dry_run=True."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        result = agent.heal_repository(dry_run=True)
        
        assert result["violations"] == 0
        assert result["fixed"] == 0
        assert result["errors"] == 0
        assert result["skipped"] == 1
    
    def test_heal_repository_execute(self):
        """Test heal_repository with execute=True."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        result = agent.heal_repository(execute=True)
        
        assert isinstance(result, dict)
        assert result["skipped"] == 1


class TestSovereignBaseAgentExecute:
    """Test execute method (abstract)."""
    
    def test_execute_not_implemented(self):
        """Test execute raises NotImplementedError."""
        agent = SovereignBaseAgent(name="TestAgent")
        
        with pytest.raises(NotImplementedError):
            agent.execute()


class TestSovereignBaseAgentInheritance:
    """Test inheritance and MRO."""
    
    def test_inherits_from_mcp_hardened_mixin(self):
        """Test SovereignBaseAgent inherits from MCPHardenedMixin."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        
        assert issubclass(SovereignBaseAgent, MCPHardenedMixin)
    
    def test_mro_order(self):
        """Test MRO has correct order."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        
        mro = SovereignBaseAgent.__mro__
        
        # Find positions
        sovereign_idx = mro.index(SovereignBaseAgent)
        mcp_idx = mro.index(MCPHardenedMixin)
        object_idx = mro.index(object)
        
        # SovereignBaseAgent -> MCPHardenedMixin -> object
        assert sovereign_idx < mcp_idx < object_idx


class TestSovereignBaseAgentDataclass:
    """Test dataclass functionality."""
    
    def test_is_dataclass(self):
        """Test SovereignBaseAgent is a dataclass."""
        from dataclasses import is_dataclass
        
        assert is_dataclass(SovereignBaseAgent)
    
    def test_dataclass_fields(self):
        """Test dataclass has expected fields."""
        from dataclasses import fields
        
        field_names = {f.name for f in fields(SovereignBaseAgent)}
        
        assert 'name' in field_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
