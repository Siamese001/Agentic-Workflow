"""ADG importability contract for apps_rg/tools/ResumeGenerator.py."""
from __future__ import annotations

import apps_rg.tools.ResumeGenerator  # noqa: F401


def test_module_importable():
    """Module ResumeGenerator must be importable."""
    assert apps_rg.tools.ResumeGenerator is not None
