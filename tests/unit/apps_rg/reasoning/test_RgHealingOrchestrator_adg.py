"""ADG importability contract for apps_rg/reasoning/RgHealingOrchestrator.py."""
from __future__ import annotations

import apps_rg.reasoning.RgHealingOrchestrator  # noqa: F401


def test_module_importable():
    """Module RgHealingOrchestrator must be importable."""
    assert apps_rg.reasoning.RgHealingOrchestrator is not None
