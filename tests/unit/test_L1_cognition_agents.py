"""Unit tests for L1 Cognition agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestL1CognitionBaseAgent:
    """Test suite for L1CognitionBaseAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create L1CognitionBaseAgent instance."""
        from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import L1CognitionBaseAgent
        return L1CognitionBaseAgent(context=mock_ctx, name="TestAgent", layer="L1")
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')


class TestDependencySentinelAgent:
    """Test suite for DependencySentinelAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create DependencySentinelAgent instance."""
        from agentic_core.L1_cognition.thought_engine.CanonDependencySentinelAgent import DependencySentinelAgent
        return DependencySentinelAgent(ctx=mock_ctx)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
