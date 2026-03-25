"""ADG-driven tests for apps_shared/enforcement/HardenedeventbusStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.HardenedeventbusStrategy  # noqa: F401


def test_module_importable():
    """Module HardenedeventbusStrategy must be importable."""
    assert apps_shared.enforcement.HardenedeventbusStrategy is not None
