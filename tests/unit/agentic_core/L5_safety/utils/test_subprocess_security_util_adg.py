"""ADG importability contract for agentic_core/L5_safety/utils/subprocess_security_util.py."""
from __future__ import annotations

import agentic_core.L5_safety.utils.subprocess_security_util  # noqa: F401


def test_module_importable():
    """Module subprocess_security_util must be importable."""
    assert agentic_core.L5_safety.utils.subprocess_security_util is not None
