"""ADG importability contract for agentic_core/L2_execution/engines/rollback_refiner.py."""
from __future__ import annotations

import agentic_core.L2_execution.engines.rollback_refiner  # noqa: F401


def test_module_importable():
    """Module rollback_refiner must be importable."""
    assert agentic_core.L2_execution.engines.rollback_refiner is not None
