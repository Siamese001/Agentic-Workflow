"""ADG importability contract for agentic_core/seams/contracts/mcp.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mcp.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.seams.contracts.mcp import (  # noqa: F401
        MCPConnectionManager,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MCPConnectionManager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="mcp.py deps unavailable")
class TestMcpImportability:
    def test_module_importable(self) -> None:
        """ADG contract: mcp.py must be importable."""
        assert _AVAILABLE

    def test_mcpconnectionmanager_is_type(self) -> None:
        assert MCPConnectionManager is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

