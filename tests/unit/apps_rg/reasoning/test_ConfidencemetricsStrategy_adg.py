"""ADG-driven tests for apps_rg/reasoning/ConfidencemetricsStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module ConfidencemetricsStrategy must be importable."""
    import apps_rg.reasoning.ConfidencemetricsStrategy  # noqa: F401

    assert apps_rg.reasoning.ConfidencemetricsStrategy is not None
