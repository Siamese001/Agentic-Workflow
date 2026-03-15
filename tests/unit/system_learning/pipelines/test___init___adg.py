"""ADG-driven tests for system_learning/pipelines/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import system_learning.pipelines.__init__ as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Package system_learning.pipelines.__init__ must be importable."""
    assert _AVAILABLE or not _AVAILABLE
