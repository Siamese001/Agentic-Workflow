"""ADG importability contract for agentic_core/L2_execution/reasoning/ToolsmithAgent.py."""
from __future__ import annotations

import agentic_core.L2_execution.reasoning.ToolsmithAgent  # noqa: F401


def test_module_importable():
    """Module ToolsmithAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.ToolsmithAgent is not None
