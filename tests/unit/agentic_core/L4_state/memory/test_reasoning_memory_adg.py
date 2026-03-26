"""ADG-driven tests for agentic_core/L4_state/memory/reasoning_memory.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.memory.reasoning_memory  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.memory.reasoning_memory  # noqa: F401
        """Module reasoning_memory must be importable."""
        assert agentic_core.L4_state.memory.reasoning_memory is not None

    assert agentic_core.L4_state.memory.reasoning_memory is not None
