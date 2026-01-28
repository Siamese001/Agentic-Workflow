# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\l1\test_UiValidationAgent.py was depth 3, MUST be 2.

#!/usr/bin/env python3
"""
Test suite for UiValidationAgent
Generated automatically to improve test coverage.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.thought_engine.UiValidationAgent import UiValidationAgent


class TestUiValidationAgent:
    """Test suite for UiValidationAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return UiValidationAgent()
    
    def test_instantiation(self, agent):
        """Test that agent can be instantiated."""
        assert agent is not None
        assert isinstance(agent, UiValidationAgent)
    
    def test_has_heal_repository(self, agent):
        """Test that agent has heal_repository method."""
        assert hasattr(agent, 'heal_repository')
        assert callable(getattr(agent, 'heal_repository'))
    
    def test_heal_repository_dry_run(self, agent):
        """Test heal_repository in dry-run mode."""
        result = agent.heal_repository(dry_run=True, execute=False)
        assert isinstance(result, dict)
        assert 'violations' in result or 'fixed' in result
    
    def test_mcp_hardened(self, agent):
        """Test that agent has MCP hardening."""
        # Check for MCPHardenedMixin in MRO
        mro_classes = [cls.__name__ for cls in type(agent).__mro__]
        assert 'MCPHardenedMixin' in mro_classes, f"Agent should have MCPHardenedMixin in MRO"
    
    def test_class_name(self, agent):
        """Test that agent has correct class name."""
        assert agent.__class__.__name__ == 'UiValidationAgent'
    
    # Add more specific tests based on agent methods
    # TODO: Expand with agent-specific test cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
