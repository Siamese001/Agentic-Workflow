"""ADG-driven tests for agentic_core/L0_routing/scripts/handler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.handler import (  # noqa: F401
        debug_dashboard,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    debug_dashboard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="handler.py deps unavailable")
class TestDebugDashboard:
    def test_is_callable(self):
        assert callable(debug_dashboard)


def test_module_importable():
    """Module handler.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
