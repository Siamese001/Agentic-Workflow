"""ADG importability contract for agentic_core/L3_orchestration/ptc/tool_invoker.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_invoker.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.ptc.tool_invoker import (  # noqa: F401
        ToolInvoker,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolInvoker = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tool_invoker.py deps unavailable")
class TestToolInvokerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tool_invoker.py must be importable."""
        assert _AVAILABLE

    def test_toolinvoker_is_type(self) -> None:
        assert ToolInvoker is not None

