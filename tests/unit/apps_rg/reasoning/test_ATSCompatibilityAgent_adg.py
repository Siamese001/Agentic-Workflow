"""ADG-driven tests for apps_rg/reasoning/ATSCompatibilityAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.reasoning.ATSCompatibilityAgent  # noqa: F401


def test_module_importable():
    """Module ATSCompatibilityAgent must be importable."""
    assert apps_rg.reasoning.ATSCompatibilityAgent is not None
