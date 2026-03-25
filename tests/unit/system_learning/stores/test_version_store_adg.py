"""ADG-driven tests for system_learning/stores/version_store.py — fan_in=2."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.stores.version_store  # noqa: F401


def test_module_importable():
    """Module version_store must be importable."""
    assert system_learning.stores.version_store is not None
