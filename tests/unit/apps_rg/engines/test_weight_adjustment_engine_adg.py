"""ADG-driven tests for apps_rg/engines/weight_adjustment_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module weight_adjustment_engine must be importable."""
    import apps_rg.engines.weight_adjustment_engine  # noqa: F401

    assert apps_rg.engines.weight_adjustment_engine is not None
