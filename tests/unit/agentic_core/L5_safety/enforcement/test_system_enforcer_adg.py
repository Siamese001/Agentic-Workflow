"""ADG importability contract for agentic_core/L5_safety/enforcement/system_enforcer.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.system_enforcer  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.system_enforcer  # noqa: F401
    """Module system_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.system_enforcer is not None
