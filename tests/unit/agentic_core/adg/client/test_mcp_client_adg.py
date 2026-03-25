"""ADG importability contract for agentic_core/adg/client/mcp_client.py."""
from __future__ import annotations

import agentic_core.adg.client.InMemoryStore  # noqa: F401


def test_module_importable():
    """Module InMemoryStore must be importable."""
    assert agentic_core.adg.client.InMemoryStore is not None
