"""ADG-driven tests for agentic_core/L4_state/caching/redis_mcp_client.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.caching.redis_mcp_client as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.caching.redis_mcp_client as _mod  # noqa: F401
    """Module redis_mcp_client must be importable."""
    assert _mod is not None
