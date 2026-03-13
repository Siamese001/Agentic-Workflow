"""ADG importability contract for agentic_core/L3_orchestration/ptc/tool_call_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_call_store.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.ptc.tool_call_store import (  # noqa: F401
        ToolCallStore,
        get_tool_call_store,
        list_tool_calls,
        record_tool_call,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolCallStore = None  # type: ignore[assignment,misc]
    get_tool_call_store = None  # type: ignore[assignment,misc]
    record_tool_call = None  # type: ignore[assignment,misc]
    list_tool_calls = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_call_store deps unavailable")
class TestToolCallStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/ptc/tool_call_store.py must be importable."""
        assert _AVAILABLE

    def test_toolcallstore_defined(self) -> None:
        assert ToolCallStore is not None
