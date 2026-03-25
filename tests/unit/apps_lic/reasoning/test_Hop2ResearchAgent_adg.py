"""ADG-driven tests for apps_lic/reasoning/Hop2ResearchAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.Hop2ResearchAgent  # noqa: F401


def test_module_importable():
    """Module Hop2ResearchAgent must be importable."""
    assert apps_lic.reasoning.Hop2ResearchAgent is not None
