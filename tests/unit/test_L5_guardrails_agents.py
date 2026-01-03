"""Unit tests for L5 Safety Guardrails agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCodeFormatterAgent:
    """Test suite for CodeFormatterAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create CodeFormatterAgent instance."""
        from agentic_core.L5_safety.guardrails.CodeFormatterAgent import CodeFormatterAgent
        return CodeFormatterAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestDependencyPruningAgent:
    """Test suite for DependencyPruningAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create DependencyPruningAgent instance."""
        from agentic_core.L5_safety.guardrails.DependencyPruningAgent import DependencyPruningAgent
        return DependencyPruningAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestDuplicateCodeDetectorAgent:
    """Test suite for DuplicateCodeDetectorAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create DuplicateCodeDetectorAgent instance."""
        from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent
        return DuplicateCodeDetectorAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestGitHygieneAgent:
    """Test suite for GitHygieneAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create GitHygieneAgent instance."""
        from agentic_core.L5_safety.guardrails.GitHygieneAgent import GitHygieneAgent
        return GitHygieneAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestGravityEnforcerAgent:
    """Test suite for GravityEnforcerAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create GravityEnforcerAgent instance."""
        from agentic_core.L5_safety.guardrails.GravityEnforcerAgent import GravityEnforcerAgent
        return GravityEnforcerAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)


class TestMCPHardenedMixin:
    """Test suite for MCPHardenedMixin."""
    
    def test_mixin_exists(self):
        """Test MCPHardenedMixin can be imported."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        assert MCPHardenedMixin is not None
    
    def test_mixin_has_heal_repository(self):
        """Test MCPHardenedMixin has heal_repository."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        assert hasattr(MCPHardenedMixin, 'heal_repository')
