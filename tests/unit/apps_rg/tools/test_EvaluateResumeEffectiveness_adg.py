"""ADG-driven tests for apps_rg/tools/EvaluateResumeEffectiveness.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.EvaluateResumeEffectiveness  # noqa: F401


def test_module_importable():
    """Module EvaluateResumeEffectiveness must be importable."""
    assert apps_rg.tools.EvaluateResumeEffectiveness is not None
