"""ADG importability contract for apps_rg/reasoning/RgResumeOrchestrator.py."""
from __future__ import annotations

import apps_rg.reasoning.RgResumeOrchestrator  # noqa: F401


def test_module_importable():
    """Module RgResumeOrchestrator must be importable."""
    assert apps_rg.reasoning.RgResumeOrchestrator is not None
