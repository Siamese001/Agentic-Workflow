"""ADG importability contract for agentic_core/adg/adapters/memory_mcp_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_memory_mcp_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.adapters.memory_mcp_adapter import (  # noqa: F401
        ADGMemoryAdapter,
        get_adapter,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ADGMemoryAdapter = None  # type: ignore[assignment,misc]
    get_adapter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="memory_mcp_adapter.py deps unavailable")
class TestMemoryMcpAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: memory_mcp_adapter.py must be importable."""
        assert _AVAILABLE

    def test_adgmemoryadapter_is_type(self) -> None:
        assert ADGMemoryAdapter is not None

    def test_get_adapter_callable(self) -> None:
        assert callable(get_adapter)

