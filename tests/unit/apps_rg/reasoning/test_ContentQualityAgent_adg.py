"""ADG importability contract for apps_rg/reasoning/ContentQualityAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.ContentQualityAgent  # noqa: F401


def test_module_importable():
    """Module ContentQualityAgent must be importable."""
    assert apps_rg.reasoning.ContentQualityAgent is not None
