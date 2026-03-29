"""ADG-driven tests for apps_lic/reasoning/CampaignBalanceAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module CampaignBalanceAgent must be importable."""
    import apps_lic.reasoning.CampaignBalanceAgent  # noqa: F401

    assert apps_lic.reasoning.CampaignBalanceAgent is not None