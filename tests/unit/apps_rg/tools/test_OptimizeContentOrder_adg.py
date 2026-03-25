"""ADG-driven tests for apps_rg/tools/OptimizeContentOrder.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.OptimizeContentOrder  # noqa: F401


def test_module_importable():
    """Module OptimizeContentOrder must be importable."""
    assert apps_rg.tools.OptimizeContentOrder is not None
