"""ADG importability contract for apps_rg/reasoning/FactCheckAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.FactCheckAgent  # noqa: F401


def test_module_importable():
    """Module FactCheckAgent must be importable."""
    assert apps_rg.reasoning.FactCheckAgent is not None
