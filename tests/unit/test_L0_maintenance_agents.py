"""Unit tests for L0 Maintenance agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMaintenanceBaseAgent:
    """Test suite for MaintenanceBaseAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create MaintenanceBaseAgent instance."""
        from agentic_core.L0_maintenance.scripts.MaintenanceBaseAgent import MaintenanceBaseAgent
        return MaintenanceBaseAgent(ctx=mock_ctx)
    
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


class TestSubAtomicAgent:
    """Test suite for SubAtomicAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create SubAtomicAgent instance."""
        from agentic_core.L2_execution.tool_registry.SubAtomicAgent import SubAtomicAgent
        return SubAtomicAgent(context=mock_ctx)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestBootstrapAgent:
    """Test suite for BootstrapAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create BootstrapAgent instance."""
        from agentic_core.L0_maintenance.scripts.BootstrapAgent import BootstrapAgent
        return BootstrapAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestHealingOrchestratorAgent:
    """Test suite for HealingOrchestratorAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create HealingOrchestratorAgent instance."""
        from agentic_core.L0_maintenance.scripts.HealingOrchestratorAgent import HealingOrchestratorAgent
        return HealingOrchestratorAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
