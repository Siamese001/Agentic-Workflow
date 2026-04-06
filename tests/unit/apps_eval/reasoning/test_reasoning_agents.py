"""Test reasoning agents for apps_eval."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQualityGateAgent:
    """Test QualityGateAgent functionality."""

    @patch("apps_eval.reasoning.QualityGateAgent.emit_replay_key")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_snapshots_state")
    def test_init_default_config(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization with default config."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        agent = QualityGateAgent()

        assert agent.config == {}
        assert agent._default_threshold == 0.70
        mock_replay.assert_called_once_with("quality_gate", "agent_init")
        mock_digest.assert_called_once_with("quality_gate", "agent_init")
        mock_guardrail.assert_called_once_with("p0", "quality_gate_agent", "agent_init")
        mock_snapshot.assert_called_once_with("p0", "quality_gate_agent", "agent_state")

    @patch("apps_eval.reasoning.QualityGateAgent.emit_replay_key")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_snapshots_state")
    def test_init_with_config(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization with custom config."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        agent = QualityGateAgent(config={"quality_threshold": 0.85})

        assert agent._default_threshold == 0.85

    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_execution_trace")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_orchestrates_workflow")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_dispatches_agent")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_telemetry_event")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_gated_by_confidence")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_replay_key")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_snapshots_state")
    @pytest.mark.asyncio
    async def test_evaluate_quality_gate_passed(
        self,
        mock_snapshot,
        mock_digest,
        mock_replay,
        mock_guardrail,
        mock_gated,
        mock_telemetry,
        mock_dispatch,
        mock_orchestrate,
        mock_trace,
    ):
        """Test quality gate evaluation when passed."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        agent = QualityGateAgent()
        results = {"overall_score": 0.85}

        result = await agent.evaluate_quality_gate(results)

        assert result["passed"] is True
        assert result["overall_score"] == 0.85
        assert result["violations"] == []
        assert "trace_id" in result

    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_execution_trace")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_orchestrates_workflow")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_dispatches_agent")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_telemetry_event")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_gated_by_confidence")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_replay_key")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_snapshots_state")
    @pytest.mark.asyncio
    async def test_evaluate_quality_gate_failed(
        self,
        mock_snapshot,
        mock_digest,
        mock_replay,
        mock_guardrail,
        mock_gated,
        mock_telemetry,
        mock_dispatch,
        mock_orchestrate,
        mock_trace,
    ):
        """Test quality gate evaluation when failed."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        agent = QualityGateAgent()
        results = {"overall_score": 0.50}

        result = await agent.evaluate_quality_gate(results)

        assert result["passed"] is False
        assert result["violations"] == ["Overall score below threshold"]
        mock_guardrail.assert_called_with("p0", "quality_gate_agent", "quality_violation")

    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_execution_trace")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_orchestrates_workflow")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_dispatches_agent")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_records_telemetry_event")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_gated_by_confidence")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_replay_key")
    @patch("apps_eval.reasoning.QualityGateAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_snapshots_state")
    @patch("apps_eval.reasoning.QualityGateAgent._emit_applies_guardrail")
    @pytest.mark.asyncio
    async def test_evaluate_quality_gate_custom_threshold(
        self,
        mock_snapshot,
        mock_digest,
        mock_replay,
        mock_guardrail,
        mock_gated,
        mock_telemetry,
        mock_dispatch,
        mock_orchestrate,
        mock_trace,
    ):
        """Test quality gate evaluation with custom threshold."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        agent = QualityGateAgent()
        results = {"overall_score": 0.75}

        result = await agent.evaluate_quality_gate(results, quality_threshold=0.80)

        assert result["passed"] is False
        assert result["threshold"] == 0.80

    def test_make_trace_id_static(self):
        """Test static trace ID generation."""
        from apps_eval.reasoning.QualityGateAgent import QualityGateAgent

        results = {"overall_score": 0.85}
        trace_id = QualityGateAgent._make_trace_id(results)

        assert isinstance(trace_id, str)
        assert len(trace_id) == 16


@pytest.mark.unit
class TestScenarioGenerationAgent:
    """Test ScenarioGenerationAgent functionality."""

    @patch("apps_eval.reasoning.ScenarioGenerationAgent.emit_replay_key")
    @patch("apps_eval.reasoning.ScenarioGenerationAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.ScenarioGenerationAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.ScenarioGenerationAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_eval.reasoning.ScenarioGenerationAgent import ScenarioGenerationAgent

        agent = ScenarioGenerationAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("scenario_gen", "agent_init")
        mock_digest.assert_called_once_with("scenario_gen", "agent_init")


@pytest.mark.unit
class TestTestDiscoveryAgent:
    """Test TestDiscoveryAgent functionality."""

    @patch("apps_eval.reasoning.TestDiscoveryAgent.emit_replay_key")
    @patch("apps_eval.reasoning.TestDiscoveryAgent.emit_determinism_digest")
    @patch("apps_eval.reasoning.TestDiscoveryAgent._emit_applies_guardrail")
    @patch("apps_eval.reasoning.TestDiscoveryAgent._emit_snapshots_state")
    def test_init(self, mock_snapshot, mock_guardrail, mock_digest, mock_replay):
        """Test initialization."""
        from apps_eval.reasoning.TestDiscoveryAgent import TestDiscoveryAgent

        agent = TestDiscoveryAgent()

        assert agent.config == {}
        mock_replay.assert_called_once_with("test_discovery", "agent_init")
        mock_digest.assert_called_once_with("test_discovery", "agent_init")
