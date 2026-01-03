"""Unit tests for ComplianceOrchestratorAgent - L5 Safety Validator."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestComplianceOrchestratorAgent:
    """Test suite for ComplianceOrchestratorAgent."""
    
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
        """Create ComplianceOrchestratorAgent instance."""
        from agentic_core.L5_safety.validators.ComplianceOrchestratorAgent import ComplianceOrchestratorAgent
        return ComplianceOrchestratorAgent(ctx=mock_ctx, project_root=Path('.'))
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
        assert hasattr(agent, 'run_full_compliance')
    
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
    
    def test_heal_repository_depth_limit(self, agent):
        """Test heal_repository respects depth limit."""
        result = agent.heal_repository(dry_run=True, depth=10, max_depth=3)
        assert result.get('depth_limited') == True


class TestComplianceOrchestratorAgentDiscovery:
    """Test agent discovery in ComplianceOrchestratorAgent."""
    
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
        """Create ComplianceOrchestratorAgent instance."""
        from agentic_core.L5_safety.validators.ComplianceOrchestratorAgent import ComplianceOrchestratorAgent
        return ComplianceOrchestratorAgent(ctx=mock_ctx, project_root=Path('.'))
    
    def test_discover_all_agents(self, agent):
        """Test agent discovery returns list."""
        if hasattr(agent, '_discover_all_agents'):
            agents = agent._discover_all_agents()
            assert isinstance(agents, (list, dict))
