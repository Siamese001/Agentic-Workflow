"""ADG importability contract for agentic_core/L0_routing/types/guardian_registry_types.py."""
from __future__ import annotations

import agentic_core.L0_routing.types.guardian_registry_types  # noqa: F401


def test_module_importable():
    """Module guardian_registry_types must be importable."""
    assert agentic_core.L0_routing.types.guardian_registry_types is not None
