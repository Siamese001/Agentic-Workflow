"""Test reasoning agents for apps_exec."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBriefAssemblyAgent:
    """Test BriefAssemblyAgent functionality."""

    @patch("apps_exec.reasoning.BriefAssemblyAgent.emit_replay_key")
    @patch("apps_exec.reasoning.BriefAssemblyAgent.emit_determinism_digest")
    @patch("apps_exec.reasoning.BriefAssemblyAgent._emit_applies_guardrail")
    @patch("apps_exec.reasoning.BriefAssemblyAgent._emit_snapshots_state")
    @patch("apps_exec.reasoning.BriefAssemblyAgent.BriefAssemblerService")
    def test_init(self, mock_service, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_exec.reasoning.BriefAssemblyAgent import BriefAssemblyAgent

        agent = BriefAssemblyAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("brief_assembly", "agent_init")
        mock_digest.assert_called_once_with("brief_assembly", "agent_init")
        mock_service.assert_called_once()

    @patch("apps_exec.reasoning.BriefAssemblyAgent.emit_replay_key")
    @patch("apps_exec.reasoning.BriefAssemblyAgent.emit_determinism_digest")
    @patch("apps_exec.reasoning.BriefAssemblyAgent._emit_applies_guardrail")
    @patch("apps_exec.reasoning.BriefAssemblyAgent._emit_snapshots_state")
    @patch("apps_exec.reasoning.BriefAssemblyAgent.BriefAssemblerService")
    def test_init_with_config(self, mock_service, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization with config."""
        from apps_exec.reasoning.BriefAssemblyAgent import BriefAssemblyAgent

        agent = BriefAssemblyAgent(config={"target_persona": "recruiter"})

        assert agent.config == {"target_persona": "recruiter"}


@pytest.mark.unit
class TestSourceIngestionAgent:
    """Test SourceIngestionAgent functionality."""

    @patch("apps_exec.reasoning.SourceIngestionAgent.emit_replay_key")
    @patch("apps_exec.reasoning.SourceIngestionAgent.emit_determinism_digest")
    @patch("apps_exec.reasoning.SourceIngestionAgent._emit_applies_guardrail")
    @patch("apps_exec.reasoning.SourceIngestionAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_exec.reasoning.SourceIngestionAgent import SourceIngestionAgent

        agent = SourceIngestionAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("source_ingestion", "agent_init")
        mock_digest.assert_called_once_with("source_ingestion", "agent_init")


@pytest.mark.unit
class TestStyleComplianceAgent:
    """Test StyleComplianceAgent functionality."""

    @patch("apps_exec.reasoning.StyleComplianceAgent.emit_replay_key")
    @patch("apps_exec.reasoning.StyleComplianceAgent.emit_determinism_digest")
    @patch("apps_exec.reasoning.StyleComplianceAgent._emit_applies_guardrail")
    @patch("apps_exec.reasoning.StyleComplianceAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_exec.reasoning.StyleComplianceAgent import StyleComplianceAgent

        agent = StyleComplianceAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("style_compliance", "agent_init")
        mock_digest.assert_called_once_with("style_compliance", "agent_init")
