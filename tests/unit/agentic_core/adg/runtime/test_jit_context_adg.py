"""ADG importability contract for agentic_core/adg/runtime/jit_context.py."""
from __future__ import annotations

import agentic_core.adg.runtime.jit_context  # noqa: F401


def test_module_importable():
    """Module jit_context must be importable."""
    assert agentic_core.adg.runtime.jit_context is not None
