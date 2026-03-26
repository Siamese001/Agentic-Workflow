"""ADG importability contract for agentic_core/L1_cognition/memory/healing_memory_retriever.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L1_cognition.memory.healing_memory_retriever  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.memory.healing_memory_retriever  # noqa: F401
    """Module healing_memory_retriever must be importable."""
    assert agentic_core.L1_cognition.memory.healing_memory_retriever is not None
