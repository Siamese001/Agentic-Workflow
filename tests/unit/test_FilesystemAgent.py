"""Unit tests for FilesystemAgent - L5 Safety Validator."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestFilesystemAgent:
    """Test suite for FilesystemAgent filesystem validation."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        ctx.report = []
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create FilesystemAgent instance."""
        from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent
        return FilesystemAgent(ctx=mock_ctx, project_root=Path('.'))
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
        assert hasattr(agent, 'run')
    
    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method is defined."""
        assert callable(getattr(agent, 'heal_repository', None))
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict structure."""
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


class TestFilesystemAgentValidation:
    """Test filesystem validation logic."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        ctx.report = []
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create FilesystemAgent instance."""
        from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent
        return FilesystemAgent(ctx=mock_ctx, project_root=Path('.'))
    
    def test_run_returns_violations_list(self, agent):
        """Test run() returns list of violations."""
        violations = agent.run()
        assert isinstance(violations, list)
