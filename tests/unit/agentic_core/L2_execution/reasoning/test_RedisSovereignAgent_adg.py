"""ADG importability contract for agentic_core/L2_execution/reasoning/RedisSovereignAgent.py."""
from __future__ import annotations

import agentic_core.L2_execution.reasoning.RedisSovereignAgent  # noqa: F401


def test_module_importable():
    """Module RedisSovereignAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.RedisSovereignAgent is not None
