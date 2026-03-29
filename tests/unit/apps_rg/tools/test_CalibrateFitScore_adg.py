"""ADG-driven tests for apps_rg/tools/CalibrateFitScore.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module CalibrateFitScore must be importable."""
    import apps_rg.tools.CalibrateFitScore  # noqa: F401

    assert apps_rg.tools.CalibrateFitScore is not None