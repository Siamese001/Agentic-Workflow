"""ADG importability contract for apps_rg/reasoning/RgStrategicPlannerAgent.py."""
from __future__ import annotations



def test_module_importable():
    """Module RgStrategicPlannerAgent must be importable."""
    import apps_rg.reasoning.RgStrategicPlannerAgent  # noqa: F401

    assert apps_rg.reasoning.RgStrategicPlannerAgent is not None