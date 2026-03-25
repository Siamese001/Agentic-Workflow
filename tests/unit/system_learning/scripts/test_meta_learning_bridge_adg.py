"""ADG-driven tests for system_learning/scripts/meta_learning_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.scripts.meta_learning_bridge  # noqa: F401


def test_module_importable():
    """Module meta_learning_bridge must be importable."""
    assert system_learning.scripts.meta_learning_bridge is not None
