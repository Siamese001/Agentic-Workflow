"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.reasoning.DAGMutatorAgent  # noqa: F401


def test_module_importable():
    """Module DAGMutatorAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.DAGMutatorAgent is not None
