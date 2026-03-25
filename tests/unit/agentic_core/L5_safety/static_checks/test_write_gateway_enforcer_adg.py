"""ADG importability contract for agentic_core/L5_safety/static_checks/write_gateway_enforcer.py."""
from __future__ import annotations

import agentic_core.L5_safety.static_checks.write_gateway_enforcer  # noqa: F401


def test_module_importable():
    """Module write_gateway_enforcer must be importable."""
    assert agentic_core.L5_safety.static_checks.write_gateway_enforcer is not None
