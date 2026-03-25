"""ADG importability contract for agentic_core/L3_orchestration/reasoning/UnifiedAgent.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.reasoning.UnifiedAgent  # noqa: F401


def test_module_importable():
    """Module UnifiedAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.UnifiedAgent is not None
