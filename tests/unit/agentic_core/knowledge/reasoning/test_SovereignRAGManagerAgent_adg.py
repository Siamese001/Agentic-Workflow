"""ADG importability contract for agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py."""
from __future__ import annotations

import agentic_core.knowledge.reasoning.SovereignRAGManagerAgent  # noqa: F401


def test_module_importable():
    """Module SovereignRAGManagerAgent must be importable."""
    assert agentic_core.knowledge.reasoning.SovereignRAGManagerAgent is not None
