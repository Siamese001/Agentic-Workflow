"""ADG importability contract for agentic_core/L5_safety/utils/gravity_visitor_util.py."""
from __future__ import annotations

import agentic_core.L5_safety.utils.gravity_visitor_util  # noqa: F401


def test_module_importable():
    """Module gravity_visitor_util must be importable."""
    assert agentic_core.L5_safety.utils.gravity_visitor_util is not None
