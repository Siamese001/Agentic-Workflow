"""ADG importability contract for agentic_core/base_agents/L3OrchestrationBase.py."""
from __future__ import annotations

import agentic_core.base_agents.L3OrchestrationBase  # noqa: F401


def test_module_importable():
    """Module L3OrchestrationBase must be importable."""
    assert agentic_core.base_agents.L3OrchestrationBase is not None
