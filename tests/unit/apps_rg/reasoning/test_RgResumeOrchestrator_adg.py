"""ADG importability contract for apps_rg/reasoning/RgResumeOrchestrator.py."""
from __future__ import annotations



def test_module_importable():
    """Module RgResumeOrchestrator must be importable."""
    import apps_rg.reasoning.RgResumeOrchestrator  # noqa: F401

    assert apps_rg.reasoning.RgResumeOrchestrator is not None
