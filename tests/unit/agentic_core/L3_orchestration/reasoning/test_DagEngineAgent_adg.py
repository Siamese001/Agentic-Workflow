"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DagEngineAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.reasoning.DagEngineAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.reasoning.DagEngineAgent  # noqa: F401
    """Module DagEngineAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.DagEngineAgent is not None
