"""ADG-driven tests for apps_rg/tools/BuildSearchFilters.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module BuildSearchFilters must be importable."""
    import apps_rg.tools.BuildSearchFilters  # noqa: F401

    assert apps_rg.tools.BuildSearchFilters is not None
