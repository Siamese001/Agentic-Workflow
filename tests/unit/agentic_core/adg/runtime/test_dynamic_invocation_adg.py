"""ADG importability contract for agentic_core/adg/runtime/dynamic_invocation.py."""
from __future__ import annotations

import agentic_core.adg.runtime.dynamic_invocation  # noqa: F401


def test_module_importable():
    """Module dynamic_invocation must be importable."""
    assert agentic_core.adg.runtime.dynamic_invocation is not None
