"""ADG importability contract for agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.reasoning.SubAtomicAgent  # noqa: F401


def test_module_importable():
    """Module SubAtomicAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.SubAtomicAgent is not None
