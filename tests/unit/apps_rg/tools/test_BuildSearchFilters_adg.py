"""ADG-driven tests for apps_rg/tools/BuildSearchFilters.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.BuildSearchFilters  # noqa: F401


def test_module_importable():
    """Module BuildSearchFilters must be importable."""
    assert apps_rg.tools.BuildSearchFilters is not None
