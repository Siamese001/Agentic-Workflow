"""ADG-driven tests for apps_lic/tools/InspectMessageQuality.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.InspectMessageQuality  # noqa: F401


def test_module_importable():
    """Module InspectMessageQuality must be importable."""
    assert apps_lic.tools.InspectMessageQuality is not None
