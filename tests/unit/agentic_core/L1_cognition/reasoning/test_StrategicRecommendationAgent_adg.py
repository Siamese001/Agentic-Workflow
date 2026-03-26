"""ADG importability contract for agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent  # noqa: F401
        """Module StrategicRecommendationAgent must be importable."""
        assert agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent is not None

    assert agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent is not None
