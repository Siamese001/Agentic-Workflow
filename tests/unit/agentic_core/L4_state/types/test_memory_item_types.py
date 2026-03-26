"""Foundational behavioral tests for agentic_core/L4_state/types/memory_item_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.types.memory_item_types  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.types.memory_item_types  # noqa: F401
    """Module memory_item_types must be importable."""
    assert agentic_core.L4_state.types.memory_item_types is not None
