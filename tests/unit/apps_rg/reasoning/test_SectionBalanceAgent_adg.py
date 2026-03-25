"""ADG importability contract for apps_rg/reasoning/SectionBalanceAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.SectionBalanceAgent  # noqa: F401


def test_module_importable():
    """Module SectionBalanceAgent must be importable."""
    assert apps_rg.reasoning.SectionBalanceAgent is not None
