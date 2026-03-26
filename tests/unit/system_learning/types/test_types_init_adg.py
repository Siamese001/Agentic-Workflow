"""ADG-driven tests for system_learning/types/__init__.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
        import system_learning.types
        assert system_learning.types is not None
        import system_learning.types
        assert hasattr(system_learning.types, "__path__")

    assert system_learning.types is not None


def test_module_is_package():
    assert hasattr(system_learning.types, "__path__")
