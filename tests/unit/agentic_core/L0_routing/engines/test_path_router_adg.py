"""ADG importability contract for agentic_core/L0_routing/engines/path_router.py."""
from __future__ import annotations

import agentic_core.L0_routing.engines.path_router  # noqa: F401


def test_module_importable():
    """Module path_router must be importable."""
    assert agentic_core.L0_routing.engines.path_router is not None
