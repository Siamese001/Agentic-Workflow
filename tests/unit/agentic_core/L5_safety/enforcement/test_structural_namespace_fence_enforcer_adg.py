"""ADG importability contract for agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.structural_namespace_fence_enforcer  # noqa: F401


def test_module_importable():
    """Module structural_namespace_fence_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.structural_namespace_fence_enforcer is not None
