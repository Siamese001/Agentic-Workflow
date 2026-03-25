"""ADG importability contract for agentic_core/L5_safety/types/surgical_context_types.py."""
from __future__ import annotations

import agentic_core.L5_safety.types.surgical_context_types  # noqa: F401


def test_module_importable():
    """Module surgical_context_types must be importable."""
    assert agentic_core.L5_safety.types.surgical_context_types is not None
