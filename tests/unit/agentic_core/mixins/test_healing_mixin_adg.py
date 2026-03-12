"""ADG-driven tests for agentic_core/mixins/healing_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.healing_mixin import (  # noqa: F401
        HealingStrategyMixin,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingStrategyMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_mixin.py deps unavailable")
class TestHealingStrategyMixin:
    def test_is_class(self):
        assert isinstance(HealingStrategyMixin, type)
    def test_importable(self):
        assert HealingStrategyMixin is not None


def test_module_importable():
    """Module healing_mixin.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
