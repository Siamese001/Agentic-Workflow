"""ADG importability contract for agentic_core/runtime/config/reasoning_types.py."""
from __future__ import annotations

import agentic_core.runtime.config.reasoning_types  # noqa: F401


def test_module_importable():
    """Module reasoning_types must be importable."""
    assert agentic_core.runtime.config.reasoning_types is not None
