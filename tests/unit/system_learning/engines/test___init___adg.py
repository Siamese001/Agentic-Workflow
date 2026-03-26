"""ADG-driven tests for system_learning/engines/__init__.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module engines must be importable."""
    import system_learning.engines.__init__ as _mod
    assert _mod is not None