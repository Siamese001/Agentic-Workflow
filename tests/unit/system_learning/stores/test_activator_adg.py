"""ADG-driven tests for system_learning/stores/activator.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module activator must be importable."""
    import system_learning.stores.activator
    assert system_learning.stores.activator is not None
