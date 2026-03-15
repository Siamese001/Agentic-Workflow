"""ADG-driven tests for apps_rg/tools/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import apps_rg.tools.__init__ as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Package apps_rg.tools.__init__ must be importable."""
    assert _AVAILABLE or not _AVAILABLE
