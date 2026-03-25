"""ADG-driven tests for system_learning/constraints/config_surfaces.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.constraints.config_surfaces  # noqa: F401


def test_module_importable():
    """Module config_surfaces must be importable."""
    assert system_learning.constraints.config_surfaces is not None
