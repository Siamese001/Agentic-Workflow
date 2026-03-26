"""ADG importability contract for agentic_core/L4_state/memory/semantic_cache_manager.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.memory.semantic_cache_manager  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.memory.semantic_cache_manager  # noqa: F401
    """Module semantic_cache_manager must be importable."""
    assert agentic_core.L4_state.memory.semantic_cache_manager is not None
