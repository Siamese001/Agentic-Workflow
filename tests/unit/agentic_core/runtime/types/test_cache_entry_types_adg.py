"""ADG importability contract for agentic_core/runtime/types/cache_entry_types.py."""
from __future__ import annotations

import agentic_core.runtime.types.cache_entry_types  # noqa: F401


def test_module_importable():
    """Module cache_entry_types must be importable."""
    assert agentic_core.runtime.types.cache_entry_types is not None
