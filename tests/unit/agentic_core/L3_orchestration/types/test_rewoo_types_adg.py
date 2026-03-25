"""ADG importability contract for agentic_core/L3_orchestration/types/rewoo_types.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.types.rewoo_types  # noqa: F401


def test_module_importable():
    """Module rewoo_types must be importable."""
    assert agentic_core.L3_orchestration.types.rewoo_types is not None
