"""ADG importability contract for agentic_core/L4_state/engines/ghost_mutation_detector.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.engines.ghost_mutation_detector  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.engines.ghost_mutation_detector  # noqa: F401
    """Module ghost_mutation_detector must be importable."""
    assert agentic_core.L4_state.engines.ghost_mutation_detector is not None
