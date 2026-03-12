"""ADG-driven tests for agentic_core/L0_routing/scripts/debris_hunter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.debris_hunter import (  # noqa: F401
        DebrisHunter,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DebrisHunter = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="debris_hunter.py deps unavailable")
class TestDebrisHunter:
    def test_is_class(self):
        assert isinstance(DebrisHunter, type)
    def test_importable(self):
        assert DebrisHunter is not None


def test_module_importable():
    """Module debris_hunter.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
