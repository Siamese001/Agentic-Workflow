"""Tests for apps_research reasoning components."""

from apps_research.reasoning.ResearchOrchestrator import (
    ResearchOrchestrator,
)
from apps_research.reasoning.SourceDiscoveryAgent import (
    SourceDiscoveryAgent,
)


class TestResearchOrchestrator:
    """Test ResearchOrchestrator."""

    def test_orchestrator_import(self):
        """Test that ResearchOrchestrator can be imported."""
        assert ResearchOrchestrator is not None

    def test_orchestrator_class_exists(self):
        """Test that ResearchOrchestrator class exists."""
        assert callable(ResearchOrchestrator)


class TestSourceDiscoveryAgent:
    """Test SourceDiscoveryAgent."""

    def test_agent_import(self):
        """Test that SourceDiscoveryAgent can be imported."""
        assert SourceDiscoveryAgent is not None

    def test_agent_class_exists(self):
        """Test that SourceDiscoveryAgent class exists."""
        assert callable(SourceDiscoveryAgent)
