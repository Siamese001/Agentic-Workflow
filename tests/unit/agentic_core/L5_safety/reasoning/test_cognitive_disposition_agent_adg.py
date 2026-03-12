"""ADG-driven tests for agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py — fan_in=4.

Contract tests: DispositionDecision, CognitiveDispositionAgent init and analytics.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import (
    CognitiveDispositionAgent,
    DispositionDecision,
)


class TestDispositionDecision:
    def test_valid_creation(self):
        d = DispositionDecision(action="MOVE", target_path="agentic_core/L5/foo.py", reason="gravity", confidence=0.9)
        assert d.action == "MOVE"
        assert d.target_path == "agentic_core/L5/foo.py"
        assert d.confidence == 0.9

    def test_defaults(self):
        d = DispositionDecision(action="DELETE")
        assert d.target_path is None
        assert d.reason == ""
        assert d.confidence == 0.0

    def test_action_stored(self):
        d = DispositionDecision(action="MANUAL_REVIEW")
        assert d.action == "MANUAL_REVIEW"


class TestCognitiveDispositionAgentInit:
    def test_creates_without_args(self):
        agent = CognitiveDispositionAgent()
        assert agent is not None

    def test_creates_with_project_root(self):
        agent = CognitiveDispositionAgent(project_root=Path("."))
        assert agent.project_root == Path(".")

    def test_default_confidence_threshold(self):
        agent = CognitiveDispositionAgent()
        assert agent.confidence_threshold == 0.75

    def test_custom_confidence_threshold(self):
        agent = CognitiveDispositionAgent(confidence_threshold=0.5)
        assert agent.confidence_threshold == 0.5

    def test_analytics_initialized(self):
        agent = CognitiveDispositionAgent()
        assert "analyses_performed" in agent.analytics
        assert agent.analytics["analyses_performed"] == 0

    def test_layer_map_populated(self):
        agent = CognitiveDispositionAgent()
        assert isinstance(agent.layer_map, dict)
        assert len(agent.layer_map) > 0


class TestCognitiveDispositionAgentAnalytics:
    def setup_method(self):
        self.agent = CognitiveDispositionAgent()

    def test_get_analytics_returns_dict(self):
        result = self.agent.get_analytics()
        assert isinstance(result, dict)

    def test_analytics_has_analyses_performed(self):
        result = self.agent.get_analytics()
        assert "analyses_performed" in result

    def test_analytics_starts_at_zero(self):
        agent = CognitiveDispositionAgent()
        result = agent.get_analytics()
        assert result["analyses_performed"] == 0

    def test_analytics_has_cache_hits(self):
        result = self.agent.get_analytics()
        assert "cache_hits" in result

    def test_analyze_violation_method_exists(self):
        assert callable(self.agent.analyze_violation)

    def test_analyze_violations_method_exists(self):
        import asyncio
        assert callable(self.agent.analyze_violations)
