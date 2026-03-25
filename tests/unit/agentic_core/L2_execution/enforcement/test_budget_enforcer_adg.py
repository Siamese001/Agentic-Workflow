"""ADG importability contract for agentic_core/L2_execution/enforcement/budget_enforcer.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.budget_enforcer  # noqa: F401


def test_module_importable():
    """Module budget_enforcer must be importable."""
    assert agentic_core.L2_execution.enforcement.budget_enforcer is not None
