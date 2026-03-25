"""ADG-driven tests for apps_lic/tools/AggregateCampaignState.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.AggregateCampaignState  # noqa: F401


def test_module_importable():
    """Module AggregateCampaignState must be importable."""
    assert apps_lic.tools.AggregateCampaignState is not None
