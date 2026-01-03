"""Unit tests for L3 Orchestration agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestFissionManagerAgent:
    """Test suite for FissionManagerAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create FissionManagerAgent instance."""
        from agentic_core.L3_orchestration.fission_logic.FissionManagerAgent import FissionManagerAgent
        return FissionManagerAgent(ctx=mock_ctx)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
    
    def test_heal_repository_cycle_detection(self, agent):
        """Test heal_repository detects cycles."""
        call_path = {agent.__class__.__name__}
        result = agent.heal_repository(dry_run=True, _call_path=call_path)
        assert result.get('cycle_detected') == True
    
    def test_heal_repository_invokes_super(self, agent):
        """Test heal_repository invokes super() for shared chain."""
        import inspect
        source = inspect.getsource(agent.heal_repository)
        assert 'super().heal_repository' in source


class TestOrchestrationBaseAgent:
    """Test suite for OrchestrationBaseAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create OrchestrationBaseAgent instance."""
        from agentic_core.L3_orchestration.workflow_engines.OrchestrationBaseAgent import OrchestrationBaseAgent
        return OrchestrationBaseAgent(ctx=mock_ctx)
    
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


class TestDAGManagerAgent:
    """Test suite for DAGManagerAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create DAGManagerAgent instance."""
        from agentic_core.L3_orchestration.workflow_engines.DAGManagerAgent import DAGManagerAgent
        return DAGManagerAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestCachedOrchestratorAgent:
    """Test suite for CachedOrchestratorAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create CachedOrchestratorAgent instance."""
        from agentic_core.L3_orchestration.workflow_engines.CachedOrchestratorAgent import CachedOrchestratorAgent
        return CachedOrchestratorAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
