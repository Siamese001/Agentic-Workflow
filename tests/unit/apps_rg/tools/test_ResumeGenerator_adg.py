"""ADG importability contract for apps_rg/tools/ResumeGenerator.py."""
from __future__ import annotations



def test_module_importable():
    """Module ResumeGenerator must be importable."""
    import apps_rg.tools.ResumeGenerator  # noqa: F401

    assert apps_rg.tools.ResumeGenerator is not None