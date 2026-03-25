"""ADG-driven tests for apps_lic/reasoning/Hop1ProfileAnalysisAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.Hop1ProfileAnalysisAgent  # noqa: F401


def test_module_importable():
    """Module Hop1ProfileAnalysisAgent must be importable."""
    assert apps_lic.reasoning.Hop1ProfileAnalysisAgent is not None
