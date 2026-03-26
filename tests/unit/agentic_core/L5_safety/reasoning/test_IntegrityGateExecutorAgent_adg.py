"""ADG importability contract for agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent  # noqa: F401
    """Module IntegrityGateExecutorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent is not None
