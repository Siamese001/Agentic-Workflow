"""ADG-driven tests for apps_lic/tools/PrioritizeTalkingPoints.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.PrioritizeTalkingPoints  # noqa: F401


def test_module_importable():
    """Module PrioritizeTalkingPoints must be importable."""
    assert apps_lic.tools.PrioritizeTalkingPoints is not None
