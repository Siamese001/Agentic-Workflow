"""ADG-driven tests for apps_lic/reasoning/Hop1ProfileAnalysisAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module Hop1ProfileAnalysisAgent must be importable."""
    import apps_lic.reasoning.Hop1ProfileAnalysisAgent  # noqa: F401

    assert apps_lic.reasoning.Hop1ProfileAnalysisAgent is not None