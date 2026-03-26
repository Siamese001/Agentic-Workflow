"""ADG-driven tests for system_learning/enforcement/boundary_guard.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module boundary_guard must be importable."""
    import system_learning.enforcement.boundary_guard
    assert system_learning.enforcement.boundary_guard is not None