"""ADG-driven tests for system_learning/stores/version_store.py — fan_in=2."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module version_store must be importable."""
    import system_learning.stores.version_store
    assert system_learning.stores.version_store is not None
