"""ADG importability contract for agentic_core/L4_state/memory/in_memory_vector_cache.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.memory.in_memory_vector_cache  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.memory.in_memory_vector_cache  # noqa: F401
    """Module in_memory_vector_cache must be importable."""
    assert agentic_core.L4_state.memory.in_memory_vector_cache is not None
