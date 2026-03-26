"""ADG-driven tests for agentic_core/L4_state/config/memory_store_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.config.memory_store_config  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.config.memory_store_config  # noqa: F401
        """Module memory_store_config must be importable."""
        assert agentic_core.L4_state.config.memory_store_config is not None

    assert agentic_core.L4_state.config.memory_store_config is not None
