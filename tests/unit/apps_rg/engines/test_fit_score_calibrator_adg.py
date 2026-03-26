"""ADG-driven tests for apps_rg/engines/fit_score_calibrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fit_score_calibrator must be importable."""
    import apps_rg.engines.fit_score_calibrator  # noqa: F401

    assert apps_rg.engines.fit_score_calibrator is not None