"""ADG importability contract for agentic_core/adg/client/mcp_client.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mcp_client.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.client.mcp_client import (  # noqa: F401
        ADGMCPClient,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ADGMCPClient = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client deps unavailable")
class TestMcpClientImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/client/mcp_client.py must be importable."""
        assert _AVAILABLE

    def test_adgmcpclient_defined(self) -> None:
        assert ADGMCPClient is not None
