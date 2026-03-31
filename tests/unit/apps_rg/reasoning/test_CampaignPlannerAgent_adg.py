"""ADG importability contract for apps_rg/reasoning/CampaignPlannerAgent.py."""
from __future__ import annotations


def test_module_importable():
    """Module CampaignPlannerAgent must be importable."""
    import apps_rg.reasoning.CampaignPlannerAgent as _mod  # noqa: F401

    assert _mod is not None
