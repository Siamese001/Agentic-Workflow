"""ADG importability contract for agentic_core/L4_state/memory/sovereign_semantic_cache.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.memory.sovereign_semantic_cache  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.memory.sovereign_semantic_cache  # noqa: F401
    """Module sovereign_semantic_cache must be importable."""
    assert agentic_core.L4_state.memory.sovereign_semantic_cache is not None
