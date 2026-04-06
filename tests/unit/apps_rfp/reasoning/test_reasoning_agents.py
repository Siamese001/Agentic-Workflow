"""Test reasoning agents for apps_rfp."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestComplianceMappingAgent:
    """Test ComplianceMappingAgent functionality."""

    @patch("apps_rfp.reasoning.ComplianceMappingAgent.emit_replay_key")
    @patch("apps_rfp.reasoning.ComplianceMappingAgent.emit_determinism_digest")
    @patch("apps_rfp.reasoning.ComplianceMappingAgent._emit_applies_guardrail")
    @patch("apps_rfp.reasoning.ComplianceMappingAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_rfp.reasoning.ComplianceMappingAgent import ComplianceMappingAgent

        agent = ComplianceMappingAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("compliance_mapping", "agent_init")
        mock_digest.assert_called_once_with("compliance_mapping", "agent_init")


@pytest.mark.unit
class TestRequirementAnalysisAgent:
    """Test RequirementAnalysisAgent functionality."""

    @patch("apps_rfp.reasoning.RequirementAnalysisAgent.emit_replay_key")
    @patch("apps_rfp.reasoning.RequirementAnalysisAgent.emit_determinism_digest")
    @patch("apps_rfp.reasoning.RequirementAnalysisAgent._emit_applies_guardrail")
    @patch("apps_rfp.reasoning.RequirementAnalysisAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_rfp.reasoning.RequirementAnalysisAgent import RequirementAnalysisAgent

        agent = RequirementAnalysisAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("req_analysis", "agent_init")
        mock_digest.assert_called_once_with("req_analysis", "agent_init")
