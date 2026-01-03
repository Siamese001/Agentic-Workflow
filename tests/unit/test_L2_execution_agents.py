"""Unit tests for L2 Execution agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCodeJanitorAgent:
    """Test suite for CodeJanitorAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create CodeJanitorAgent instance."""
        from agentic_core.L2_execution.ToolRegistry.CodeJanitorAgent import CodeJanitorAgent
        return CodeJanitorAgent(ctx=mock_ctx)
    
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


class TestStructuralEngineerAgent:
    """Test suite for StructuralEngineerAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create StructuralEngineerAgent instance."""
        from agentic_core.L2_execution.ToolRegistry.StructuralEngineerAgent import StructuralEngineerAgent
        return StructuralEngineerAgent(ctx=mock_ctx)
    
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


class TestSystemArchitectAgent:
    """Test suite for SystemArchitectAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create SystemArchitectAgent instance."""
        from agentic_core.L2_execution.ToolRegistry.SystemArchitectAgent import SystemArchitectAgent
        return SystemArchitectAgent(ctx=mock_ctx)
    
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


class TestGitAgent:
    """Test suite for GitAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create GitAgent instance."""
        from agentic_core.L2_execution.ToolRegistry.GitAgent import GitAgent
        return GitAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestContextCuratorAgent:
    """Test suite for ContextCuratorAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create ContextCuratorAgent instance."""
        from agentic_core.L2_execution.ToolRegistry.ContextCuratorAgent import ContextCuratorAgent
        return ContextCuratorAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
