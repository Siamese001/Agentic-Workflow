"""ADG-driven tests for apps_rg/engines/experience_weighting_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module experience_weighting_engine must be importable."""
    import apps_rg.engines.experience_weighting_engine  # noqa: F401

    assert apps_rg.engines.experience_weighting_engine is not None