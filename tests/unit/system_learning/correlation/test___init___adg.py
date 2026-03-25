"""ADG-driven tests for system_learning/correlation/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.correlation.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module correlation must be importable."""
    assert _mod is not None
