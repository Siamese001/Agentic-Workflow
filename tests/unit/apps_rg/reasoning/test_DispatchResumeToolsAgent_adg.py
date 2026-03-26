"""ADG importability contract for apps_rg/reasoning/DispatchResumeToolsAgent.py."""
from __future__ import annotations



def test_module_importable():
    """Module DispatchResumeToolsAgent must be importable."""
    import apps_rg.reasoning.DispatchResumeToolsAgent  # noqa: F401

    assert apps_rg.reasoning.DispatchResumeToolsAgent is not None
