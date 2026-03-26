"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.SafetyDetectorAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.SafetyDetectorAgent  # noqa: F401
        """Module SafetyDetectorAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.SafetyDetectorAgent is not None

    assert agentic_core.L5_safety.reasoning.SafetyDetectorAgent is not None
