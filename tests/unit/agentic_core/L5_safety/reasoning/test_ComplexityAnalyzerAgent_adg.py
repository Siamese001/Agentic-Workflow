"""ADG importability contract for agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent  # noqa: F401


def test_module_importable():
    """Module ComplexityAnalyzerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent is not None
