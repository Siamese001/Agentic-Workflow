"""ADG-driven tests for system_learning/validators/readonly_access.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module readonly_access must be importable."""
    import system_learning.validators.readonly_access
    assert system_learning.validators.readonly_access is not None