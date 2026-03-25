"""ADG importability contract for agentic_core/adg/runtime/capability_budget.py."""
from __future__ import annotations

import agentic_core.adg.runtime.capability_budget  # noqa: F401


def test_module_importable():
    """Module capability_budget must be importable."""
    assert agentic_core.adg.runtime.capability_budget is not None
