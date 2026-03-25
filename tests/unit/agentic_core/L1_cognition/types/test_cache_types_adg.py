"""ADG importability contract for agentic_core/L1_cognition/types/cache_types.py."""
from __future__ import annotations

import agentic_core.L1_cognition.types.cache_types  # noqa: F401


def test_module_importable():
    """Module cache_types must be importable."""
    assert agentic_core.L1_cognition.types.cache_types is not None
