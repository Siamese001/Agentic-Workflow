"""ADG-driven tests for system_learning/constraints/config_surfaces.py — fan_in=1."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module config_surfaces must be importable."""
    import system_learning.constraints.config_surfaces
    assert system_learning.constraints.config_surfaces is not None
