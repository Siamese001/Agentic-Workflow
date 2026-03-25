"""ADG-driven tests for apps_rg/engines/achievement_prioritizer_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.achievement_prioritizer_engine  # noqa: F401


def test_module_importable():
    """Module achievement_prioritizer_engine must be importable."""
    assert apps_rg.engines.achievement_prioritizer_engine is not None
