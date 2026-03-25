"""ADG importability contract for agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.engines.reasoning_intensity_enforcer  # noqa: F401


def test_module_importable():
    """Module reasoning_intensity_enforcer must be importable."""
    assert agentic_core.L3_orchestration.engines.reasoning_intensity_enforcer is not None
