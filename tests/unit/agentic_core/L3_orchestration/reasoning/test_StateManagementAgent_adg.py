"""ADG importability contract for agentic_core/L3_orchestration/reasoning/StateManagementAgent.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.reasoning.StateManagementAgent  # noqa: F401


def test_module_importable():
    """Module StateManagementAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.StateManagementAgent is not None
