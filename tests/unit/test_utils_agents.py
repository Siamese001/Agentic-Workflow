"""Unit tests for Utils agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestNamingAgentHealing:
    """Test suite for NamingAgent healing functionality."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create NamingAgent instance."""
        from agentic_core.utils.core_extensions.NamingAgent import NamingAgent
        return NamingAgent(ctx=mock_ctx)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
    
    def test_heal_repository_invokes_super(self, agent):
        """Test heal_repository invokes super() for shared chain."""
        import inspect
        source = inspect.getsource(agent.heal_repository)
        assert 'super().heal_repository' in source


class TestPascalSovereigntyEnforcerAgent:
    """Test suite for PascalSovereigntyEnforcerAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create PascalSovereigntyEnforcerAgent instance."""
        from agentic_core.config.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
        return PascalSovereigntyEnforcerAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
    
    def test_heal_repository_invokes_super(self, agent):
        """Test heal_repository invokes super() for shared chain."""
        import inspect
        source = inspect.getsource(agent.heal_repository)
        assert 'super().heal_repository' in source
