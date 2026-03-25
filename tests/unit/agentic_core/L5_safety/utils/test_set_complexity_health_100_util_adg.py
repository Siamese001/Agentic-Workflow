"""ADG-driven tests for agentic_core/L5_safety/utils/set_complexity_health_100_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.utils.set_complexity_health_100_util  # noqa: F401


def test_module_importable():
    """Module set_complexity_health_100_util must be importable."""
    assert agentic_core.L5_safety.utils.set_complexity_health_100_util is not None
