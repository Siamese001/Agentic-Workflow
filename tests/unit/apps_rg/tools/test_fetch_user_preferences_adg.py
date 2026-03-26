"""ADG-driven tests for apps_rg/tools/fetch_user_preferences.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fetch_user_preferences must be importable."""
    import apps_rg.tools.fetch_user_preferences  # noqa: F401

    assert apps_rg.tools.fetch_user_preferences is not None
