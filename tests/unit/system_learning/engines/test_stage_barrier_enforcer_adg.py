"""ADG importability contract for system_learning/engines/stage_barrier_enforcer.py."""
from __future__ import annotations

def test_module_importable():
    """Module stage_barrier_enforcer must be importable."""
    import system_learning.engines.stage_barrier_enforcer
    assert system_learning.engines.stage_barrier_enforcer is not None