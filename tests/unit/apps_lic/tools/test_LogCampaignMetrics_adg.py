"""ADG-driven tests for apps_lic/tools/LogCampaignMetrics.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.LogCampaignMetrics  # noqa: F401


def test_module_importable():
    """Module LogCampaignMetrics must be importable."""
    assert apps_lic.tools.LogCampaignMetrics is not None
