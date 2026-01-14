# tests/unit/test_prompt_governance_test_constitutional_logic.py
"""Unit tests for Constitutional Logic in Prompt Governance."""
from __future__ import annotations
import pytest

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


class TestConstitutionalLogic:
    """Test constitutional logic module."""

    def test_prompt_governance_directory_exists(self):
        """Test prompt_governance directory exists."""
        import os
        path = os.path.join(os.path.dirname(__file__), '..', '..', AGENTIC_CORE_DIR, 'prompt_governance')
        assert os.path.isdir(path)

    def test_constitutional_reviewer_importable(self):
        """Test ConstitutionalReviewerAgent can be imported."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        assert ConstitutionalReviewerAgent is not None

    def test_constitutional_reviewer_inherits_safety_base(self):
        """Test ConstitutionalReviewerAgent inherits from L5SafetyBaseAgent."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        from agentic_core.L5_safety.guardrails.L5SafetyBaseAgent import L5SafetyBaseAgent
        assert issubclass(ConstitutionalReviewerAgent, L5SafetyBaseAgent)
