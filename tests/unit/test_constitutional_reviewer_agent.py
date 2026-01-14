# tests/unit/test_constitutional_reviewer_agent.py
"""Unit tests for ConstitutionalReviewerAgent - L5 Safety."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestConstitutionalReviewerAgentImport:
    """Test suite for ConstitutionalReviewerAgent import and structure."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        assert ConstitutionalReviewerAgent is not None

    def test_agent_has_required_attributes(self):
        """Test agent class has expected attributes."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        assert hasattr(ConstitutionalReviewerAgent, 'run_async') or hasattr(ConstitutionalReviewerAgent, 'run')
        assert hasattr(ConstitutionalReviewerAgent, 'heal_repository')

    def test_agent_inherits_from_safety_base(self):
        """Test agent inherits from L5SafetyBaseAgent."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        from agentic_core.L5_safety.guardrails.L5SafetyBaseAgent import L5SafetyBaseAgent
        assert issubclass(ConstitutionalReviewerAgent, L5SafetyBaseAgent)
