"""ADG importability contract for apps_rg/reasoning/RgReflectionAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.RgReflectionAgent  # noqa: F401


def test_module_importable():
    """Module RgReflectionAgent must be importable."""
    assert apps_rg.reasoning.RgReflectionAgent is not None
