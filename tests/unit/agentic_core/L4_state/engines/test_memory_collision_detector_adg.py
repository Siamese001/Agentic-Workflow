"""ADG importability contract for agentic_core/L4_state/engines/memory_collision_detector.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.engines.memory_collision_detector  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.engines.memory_collision_detector  # noqa: F401
    """Module memory_collision_detector must be importable."""
    assert agentic_core.L4_state.engines.memory_collision_detector is not None
