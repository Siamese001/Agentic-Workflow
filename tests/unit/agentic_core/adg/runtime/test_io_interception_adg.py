"""ADG importability contract for agentic_core/adg/runtime/io_interception.py."""
from __future__ import annotations

import agentic_core.adg.runtime.io_interception  # noqa: F401


def test_module_importable():
    """Module io_interception must be importable."""
    assert agentic_core.adg.runtime.io_interception is not None
