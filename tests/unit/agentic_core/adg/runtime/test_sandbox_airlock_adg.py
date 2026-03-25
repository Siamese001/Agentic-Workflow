"""ADG importability contract for agentic_core/adg/runtime/sandbox_airlock.py."""
from __future__ import annotations

import agentic_core.adg.runtime.sandbox_airlock  # noqa: F401


def test_module_importable():
    """Module sandbox_airlock must be importable."""
    assert agentic_core.adg.runtime.sandbox_airlock is not None
