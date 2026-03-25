"""ADG importability contract for agentic_core/L3_orchestration/ptc/tool_call_store.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.ptc.tool_call_store  # noqa: F401


def test_module_importable():
    """Module tool_call_store must be importable."""
    assert agentic_core.L3_orchestration.ptc.tool_call_store is not None
