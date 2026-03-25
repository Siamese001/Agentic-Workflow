"""ADG importability contract for apps_rg/reasoning/ContentStrategyAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.ContentStrategyAgent  # noqa: F401


def test_module_importable():
    """Module ContentStrategyAgent must be importable."""
    assert apps_rg.reasoning.ContentStrategyAgent is not None
