"""ADG-driven tests for system_learning/runtime/isolation_monitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.runtime.isolation_monitor  # noqa: F401


def test_module_importable():
    """Module isolation_monitor must be importable."""
    assert system_learning.runtime.isolation_monitor is not None
