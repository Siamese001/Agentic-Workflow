"""ADG importability contract for agentic_core/runtime/config/capability_gap_types.py."""
from __future__ import annotations

import agentic_core.runtime.config.capability_gap_types  # noqa: F401


def test_module_importable():
    """Module capability_gap_types must be importable."""
    assert agentic_core.runtime.config.capability_gap_types is not None
