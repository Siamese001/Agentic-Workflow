"""ADG importability contract for apps_rg/reasoning/ProactiveAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.ProactiveAgent  # noqa: F401


def test_module_importable():
    """Module ProactiveAgent must be importable."""
    assert apps_rg.reasoning.ProactiveAgent is not None
