"""ADG-driven tests for apps_lic/tools/CalibrateEngagementScore.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.CalibrateEngagementScore  # noqa: F401


def test_module_importable():
    """Module CalibrateEngagementScore must be importable."""
    assert apps_lic.tools.CalibrateEngagementScore is not None
