"""ADG importability contract for system_learning/engines/stage_barrier_enforcer.py."""
from __future__ import annotations

import system_learning.engines.stage_barrier_enforcer  # noqa: F401


def test_module_importable():
    """Module stage_barrier_enforcer must be importable."""
    assert system_learning.engines.stage_barrier_enforcer is not None
