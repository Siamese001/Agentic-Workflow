"""Unit tests for base agent classes."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSovereignBaseAgent:
    """Test suite for SovereignBaseAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    def test_sovereign_base_agent_exists(self):
        """Test SovereignBaseAgent can be imported."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        assert SovereignBaseAgent is not None
    
    def test_sovereign_base_agent_has_heal_repository(self):
        """Test SovereignBaseAgent has heal_repository method."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        assert hasattr(SovereignBaseAgent, 'heal_repository')
    
    def test_heal_repository_invokes_super(self):
        """Test heal_repository invokes super() for shared chain."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        import inspect
        source = inspect.getsource(SovereignBaseAgent.heal_repository)
        assert 'super().heal_repository' in source


class TestL0Agent:
    """Test suite for L0Agent base class."""
    
    def test_l0_agent_exists(self):
        """Test L0Agent can be imported."""
        from agentic_core.bases.l0_agent import L0Agent
        assert L0Agent is not None
    
    def test_l0_agent_has_heal_repository(self):
        """Test L0Agent has heal_repository method."""
        from agentic_core.bases.l0_agent import L0Agent
        assert hasattr(L0Agent, 'heal_repository')
    
    def test_heal_repository_invokes_super(self):
        """Test heal_repository invokes super() for shared chain."""
        from agentic_core.bases.l0_agent import L0Agent
        import inspect
        source = inspect.getsource(L0Agent.heal_repository)
        assert 'super().heal_repository' in source


class TestL2Agent:
    """Test suite for L2Agent base class."""
    
    def test_l2_agent_exists(self):
        """Test L2Agent can be imported."""
        from agentic_core.bases.l2_agent import L2Agent
        assert L2Agent is not None
    
    def test_l2_agent_has_heal_repository(self):
        """Test L2Agent has heal_repository method."""
        from agentic_core.bases.l2_agent import L2Agent
        assert hasattr(L2Agent, 'heal_repository')
    
    def test_heal_repository_invokes_super(self):
        """Test heal_repository invokes super() for shared chain."""
        from agentic_core.bases.l2_agent import L2Agent
        import inspect
        source = inspect.getsource(L2Agent.heal_repository)
        assert 'super().heal_repository' in source


class TestHealerMixin:
    """Test suite for HealerMixin."""
    
    def test_healer_mixin_exists(self):
        """Test HealerMixin can be imported."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert HealerMixin is not None
    
    def test_healer_mixin_has_heal_repository(self):
        """Test HealerMixin has heal_repository method."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert hasattr(HealerMixin, 'heal_repository')
