# tests/unit/test_prompt_governance_test_constitutional_logic.py
"""Unit tests for Constitutional Logic in Prompt Governance."""
from __future__ import annotations
import pytest


class TestConstitutionalLogic:
    """Test constitutional logic module."""

    def test_prompt_governance_directory_exists(self):
        """Test prompt_governance directory exists."""
        import os
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'agentic_core', 'prompt_governance')
        assert os.path.isdir(path)

    def test_constitutional_reviewer_importable(self):
        """Test ConstitutionalReviewerAgent can be imported."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        assert ConstitutionalReviewerAgent is not None

    def test_constitutional_reviewer_inherits_safety_base(self):
        """Test ConstitutionalReviewerAgent inherits from SafetyBaseAgent."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        from agentic_core.L5_safety.guardrails.SafetyBaseAgent import SafetyBaseAgent
        assert issubclass(ConstitutionalReviewerAgent, SafetyBaseAgent)
