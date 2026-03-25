"""ADG importability contract for agentic_core/L5_safety/reasoning/BenchmarkingAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.BenchmarkingAgent  # noqa: F401


def test_module_importable():
    """Module BenchmarkingAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.BenchmarkingAgent is not None
