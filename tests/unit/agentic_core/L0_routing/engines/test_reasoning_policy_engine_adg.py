"""ADG importability contract for agentic_core/L0_routing/engines/reasoning_policy_engine.py."""
from __future__ import annotations

import agentic_core.L0_routing.engines.reasoning_policy_engine  # noqa: F401


def test_module_importable():
    """Module reasoning_policy_engine must be importable."""
    assert agentic_core.L0_routing.engines.reasoning_policy_engine is not None
