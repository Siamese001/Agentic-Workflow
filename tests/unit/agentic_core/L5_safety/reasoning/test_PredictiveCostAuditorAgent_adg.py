"""ADG importability contract for agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent  # noqa: F401
    """Module PredictiveCostAuditorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent is not None
