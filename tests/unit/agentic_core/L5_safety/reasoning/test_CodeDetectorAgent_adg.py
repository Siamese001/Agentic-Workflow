"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeDetectorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.CodeDetectorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.CodeDetectorAgent  # noqa: F401
    """Module CodeDetectorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeDetectorAgent is not None
