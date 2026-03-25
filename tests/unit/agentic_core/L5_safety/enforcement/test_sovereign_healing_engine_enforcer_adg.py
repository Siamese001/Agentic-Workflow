"""ADG importability contract for agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer  # noqa: F401


def test_module_importable():
    """Module sovereign_healing_engine_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer is not None
