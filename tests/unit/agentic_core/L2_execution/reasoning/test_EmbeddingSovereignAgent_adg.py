"""ADG importability contract for agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py."""
from __future__ import annotations

import agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent  # noqa: F401


def test_module_importable():
    """Module EmbeddingSovereignAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent is not None
