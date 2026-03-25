"""ADG-driven tests for apps_lic/tools/BuildMessageFilters.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.BuildMessageFilters  # noqa: F401


def test_module_importable():
    """Module BuildMessageFilters must be importable."""
    assert apps_lic.tools.BuildMessageFilters is not None
