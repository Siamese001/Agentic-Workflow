"""ADG-driven tests for apps_rg/engines/search_filter_builder.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.search_filter_builder  # noqa: F401


def test_module_importable():
    """Module search_filter_builder must be importable."""
    assert apps_rg.engines.search_filter_builder is not None
