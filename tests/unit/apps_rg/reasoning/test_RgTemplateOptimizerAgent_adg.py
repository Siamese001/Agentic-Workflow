"""ADG importability contract for apps_rg/reasoning/RgTemplateOptimizerAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.RgTemplateOptimizerAgent  # noqa: F401


def test_module_importable():
    """Module RgTemplateOptimizerAgent must be importable."""
    assert apps_rg.reasoning.RgTemplateOptimizerAgent is not None
