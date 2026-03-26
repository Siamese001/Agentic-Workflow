"""ADG-driven tests for agentic_core/L4_state/memory/sovereign_memory_store.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.memory.sovereign_memory_store  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.memory.sovereign_memory_store  # noqa: F401
        """Module sovereign_memory_store must be importable."""
        assert agentic_core.L4_state.memory.sovereign_memory_store is not None

    assert agentic_core.L4_state.memory.sovereign_memory_store is not None
