"""ADG-driven tests for apps_rg/tools/RefineResumeRanking.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module RefineResumeRanking must be importable."""
    import apps_rg.tools.RefineResumeRanking  # noqa: F401

    assert apps_rg.tools.RefineResumeRanking is not None