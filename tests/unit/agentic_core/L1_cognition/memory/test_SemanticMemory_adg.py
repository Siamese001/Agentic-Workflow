"""ADG importability contract for agentic_core/L1_cognition/memory/SemanticMemory.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L1_cognition.memory.SemanticMemory  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.memory.SemanticMemory  # noqa: F401
    """Module SemanticMemory must be importable."""
    assert agentic_core.L1_cognition.memory.SemanticMemory is not None
