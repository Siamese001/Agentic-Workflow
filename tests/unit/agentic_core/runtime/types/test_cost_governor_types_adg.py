"""ADG importability contract for agentic_core/runtime/types/cost_governor_types.py."""
from __future__ import annotations

import agentic_core.runtime.types.cost_governor_types  # noqa: F401


def test_module_importable():
    """Module cost_governor_types must be importable."""
    assert agentic_core.runtime.types.cost_governor_types is not None
