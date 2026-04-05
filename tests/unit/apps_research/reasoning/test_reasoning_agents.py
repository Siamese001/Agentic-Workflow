"""Test reasoning agents for apps_research."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInsightExtractionAgent:
    """Test InsightExtractionAgent functionality."""

    @patch("apps_research.reasoning.InsightExtractionAgent.emit_replay_key")
    @patch("apps_research.reasoning.InsightExtractionAgent.emit_determinism_digest")
    @patch("apps_research.reasoning.InsightExtractionAgent._emit_applies_guardrail")
    @patch("apps_research.reasoning.InsightExtractionAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_research.reasoning.InsightExtractionAgent import InsightExtractionAgent

        agent = InsightExtractionAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("insight_extraction", "agent_init")
        mock_digest.assert_called_once_with("insight_extraction", "agent_init")


@pytest.mark.unit
class TestKnowledgeSynthesisAgent:
    """Test KnowledgeSynthesisAgent functionality."""

    @patch("apps_research.reasoning.KnowledgeSynthesisAgent.emit_replay_key")
    @patch("apps_research.reasoning.KnowledgeSynthesisAgent.emit_determinism_digest")
    @patch("apps_research.reasoning.KnowledgeSynthesisAgent._emit_applies_guardrail")
    @patch("apps_research.reasoning.KnowledgeSynthesisAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_research.reasoning.KnowledgeSynthesisAgent import KnowledgeSynthesisAgent

        agent = KnowledgeSynthesisAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("knowledge_synthesis", "agent_init")
        mock_digest.assert_called_once_with("knowledge_synthesis", "agent_init")


@pytest.mark.unit
class TestSourceDiscoveryAgent:
    """Test SourceDiscoveryAgent functionality."""

    @patch("apps_research.reasoning.SourceDiscoveryAgent.emit_replay_key")
    @patch("apps_research.reasoning.SourceDiscoveryAgent.emit_determinism_digest")
    @patch("apps_research.reasoning.SourceDiscoveryAgent._emit_applies_guardrail")
    @patch("apps_research.reasoning.SourceDiscoveryAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_research.reasoning.SourceDiscoveryAgent import SourceDiscoveryAgent

        agent = SourceDiscoveryAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("source_discovery", "agent_init")
        mock_digest.assert_called_once_with("source_discovery", "agent_init")