"""Unit tests for DocstringComplianceAgent - L5 Safety Validator."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestDocstringComplianceAgent:
    """Test suite for DocstringComplianceAgent docstring validation."""
    
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
        """Create DocstringComplianceAgent instance."""
        from agentic_core.L5_safety.validators.DocstringComplianceAgent import DocstringComplianceAgent
        return DocstringComplianceAgent(ctx=mock_ctx, project_root=Path('.'))
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
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
