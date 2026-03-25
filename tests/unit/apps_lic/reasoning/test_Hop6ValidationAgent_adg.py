"""ADG-driven tests for apps_lic/reasoning/Hop6ValidationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.Hop6ValidationAgent  # noqa: F401


def test_module_importable():
    """Module Hop6ValidationAgent must be importable."""
    assert apps_lic.reasoning.Hop6ValidationAgent is not None
