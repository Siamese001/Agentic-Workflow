"""ADG-driven tests for apps_rg/reasoning/ExecutiveSummaryOutputAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module ExecutiveSummaryOutputAgent must be importable."""
    import apps_rg.reasoning.ExecutiveSummaryOutputAgent  # noqa: F401

    assert apps_rg.reasoning.ExecutiveSummaryOutputAgent is not None