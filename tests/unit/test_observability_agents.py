"""Unit tests for Observability agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMetricsAgent:
    """Test suite for MetricsAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create MetricsAgent instance."""
        from agentic_core.observability.metrics.MetricsAgent import MetricsAgent
        return MetricsAgent(ctx=mock_ctx)
    
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


class TestTelemetryAgent:
    """Test suite for TelemetryAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create TelemetryAgent instance."""
        from agentic_core.observability.telemetry.TelemetryAgent import TelemetryAgent
        return TelemetryAgent(ctx=mock_ctx)
    
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


class TestTracingAgent:
    """Test suite for TracingAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create TracingAgent instance."""
        from agentic_core.observability.tracing.TracingAgent import TracingAgent
        return TracingAgent(ctx=mock_ctx)
    
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


class TestReportingAgent:
    """Test suite for ReportingAgent."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = MagicMock()
        ctx.python_files = []
        ctx.signals = set()
        return ctx
    
    @pytest.fixture
    def agent(self, mock_ctx):
        """Create ReportingAgent instance."""
        from agentic_core.observability.compliance.ReportingAgent import ReportingAgent
        return ReportingAgent(ctx=mock_ctx)
    
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
