"""ADG-driven tests for apps_rg/enforcement/SovereigncontextStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.enforcement.SovereigncontextStrategy  # noqa: F401


def test_module_importable():
    """Module SovereigncontextStrategy must be importable."""
    assert apps_rg.enforcement.SovereigncontextStrategy is not None
