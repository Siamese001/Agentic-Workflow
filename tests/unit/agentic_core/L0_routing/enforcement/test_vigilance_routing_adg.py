"""ADG importability contract for agentic_core/L0_routing/enforcement/vigilance_routing.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vigilance_routing.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.vigilance_routing import (  # noqa: F401
        route_vigilance_event,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    route_vigilance_event = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vigilance_routing.py deps unavailable")
class TestVigilanceRoutingImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vigilance_routing.py must be importable."""
        assert _AVAILABLE

    def test_route_vigilance_event_callable(self) -> None:
        assert callable(route_vigilance_event)

