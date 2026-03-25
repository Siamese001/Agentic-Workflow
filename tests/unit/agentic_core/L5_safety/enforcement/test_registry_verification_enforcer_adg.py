"""ADG importability contract for agentic_core/L5_safety/enforcement/registry_verification_enforcer.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.registry_verification_enforcer  # noqa: F401


def test_module_importable():
    """Module registry_verification_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.registry_verification_enforcer is not None
