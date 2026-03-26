"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.SafetyExecutorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.SafetyExecutorAgent  # noqa: F401
    """Module SafetyExecutorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SafetyExecutorAgent is not None
