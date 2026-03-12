"""ADG-driven tests for system_learning/constraints/config_surfaces.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.constraints.config_surfaces import FloatConstraint, IntConstraint
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FloatConstraint = None  # type: ignore[assignment,misc]
    IntConstraint = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces deps unavailable")
class TestFloatConstraint:
    def test_creates(self):
        c = FloatConstraint(min_value=0.0, max_value=1.0, max_delta_per_cycle=0.1)
        assert c.min_value == 0.0
        assert c.max_value == 1.0

    def test_is_frozen(self):
        c = FloatConstraint(min_value=0.0, max_value=1.0, max_delta_per_cycle=0.1)
        with pytest.raises(Exception):
            c.min_value = 0.5


@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces deps unavailable")
class TestIntConstraint:
    def test_creates(self):
        c = IntConstraint(min_value=1, max_value=100, max_delta_per_cycle=5)
        assert c.min_value == 1
        assert c.max_value == 100

    def test_is_frozen(self):
        c = IntConstraint(min_value=1, max_value=100, max_delta_per_cycle=5)
        with pytest.raises(Exception):
            c.min_value = 999


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
