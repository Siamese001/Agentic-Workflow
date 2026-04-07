"""Tests for apps_rfp reasoning components."""


from apps_rfp.reasoning.RequirementAnalysisAgent import (
    RequirementAnalysisAgent,
)
from apps_rfp.reasoning.RfpOrchestrator import (
    RfpOrchestrator,
)


class TestRfpOrchestrator:
    """Test RfpOrchestrator."""

    def test_orchestrator_import(self):
        """Test that RfpOrchestrator can be imported."""
        assert RfpOrchestrator is not None

    def test_orchestrator_class_exists(self):
        """Test that RfpOrchestrator class exists."""
        assert callable(RfpOrchestrator)


class TestRequirementAnalysisAgent:
    """Test RequirementAnalysisAgent."""

    def test_agent_import(self):
        """Test that RequirementAnalysisAgent can be imported."""
        assert RequirementAnalysisAgent is not None

    def test_agent_class_exists(self):
        """Test that RequirementAnalysisAgent class exists."""
        assert callable(RequirementAnalysisAgent)
