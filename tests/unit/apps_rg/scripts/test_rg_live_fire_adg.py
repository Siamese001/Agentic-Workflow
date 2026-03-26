"""ADG-driven tests for apps_rg/scripts/rg_live_fire.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module rg_live_fire must be importable."""
    import apps_rg.scripts.rg_live_fire  # noqa: F401

    assert apps_rg.scripts.rg_live_fire is not None