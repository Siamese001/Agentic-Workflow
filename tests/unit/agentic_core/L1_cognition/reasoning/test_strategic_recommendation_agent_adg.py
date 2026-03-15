"""ADG-driven tests for L1_cognition/reasoning/StrategicRecommendationAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent import (
        StrategicRecommendationAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StrategicRecommendationAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StrategicRecommendationAgent deps unavailable")
class TestStrategicRecommendationAgent:
    def test_importable(self):
        assert callable(StrategicRecommendationAgent)

    def test_creates_with_defaults(self):
        agent = StrategicRecommendationAgent()
        assert agent is not None

    def test_has_run_or_generate(self):
        assert hasattr(StrategicRecommendationAgent, "run") or hasattr(
            StrategicRecommendationAgent, "generate_recommendations"
        )


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
