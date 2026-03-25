"""ADG importability contract for agentic_core/adg/adapters/memory_mcp_adapter.py."""
from __future__ import annotations

import agentic_core.adg.adapters.ADGMemoryAdapter  # noqa: F401


def test_module_importable():
    """Module ADGMemoryAdapter must be importable."""
    assert agentic_core.adg.adapters.ADGMemoryAdapter is not None
