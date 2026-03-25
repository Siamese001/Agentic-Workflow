"""ADG-driven tests for apps_rg/tools/ComputeSkillSimilarity.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.ComputeSkillSimilarity  # noqa: F401


def test_module_importable():
    """Module ComputeSkillSimilarity must be importable."""
    assert apps_rg.tools.ComputeSkillSimilarity is not None
