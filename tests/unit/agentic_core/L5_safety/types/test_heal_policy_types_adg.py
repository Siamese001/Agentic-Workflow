"""ADG importability contract for agentic_core/L5_safety/types/heal_policy_types.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.types.heal_policy_types  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.types.heal_policy_types  # noqa: F401
    """Module heal_policy_types must be importable."""
    assert agentic_core.L5_safety.types.heal_policy_types is not None
