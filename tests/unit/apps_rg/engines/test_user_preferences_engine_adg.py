"""ADG-driven tests for apps_rg/engines/user_preferences_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.user_preferences_engine  # noqa: F401


def test_module_importable():
    """Module user_preferences_engine must be importable."""
    assert apps_rg.engines.user_preferences_engine is not None
