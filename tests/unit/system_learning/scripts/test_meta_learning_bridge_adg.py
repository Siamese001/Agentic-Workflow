"""ADG-driven tests for system_learning/scripts/meta_learning_bridge.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module meta_learning_bridge must be importable."""
    import system_learning.scripts.meta_learning_bridge
    assert system_learning.scripts.meta_learning_bridge is not None
