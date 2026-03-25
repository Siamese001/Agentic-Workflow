"""ADG importability contract for agentic_core/L0_routing/scripts/execution.py."""
from __future__ import annotations

import agentic_core.L0_routing.scripts.execution  # noqa: F401


def test_module_importable():
    """Module execution must be importable."""
    assert agentic_core.L0_routing.scripts.execution is not None
