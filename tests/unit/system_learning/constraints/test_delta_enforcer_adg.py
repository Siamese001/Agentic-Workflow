"""ADG importability contract for system_learning/constraints/delta_enforcer.py."""
from __future__ import annotations

def test_module_importable():
    """Module delta_enforcer must be importable."""
    import system_learning.constraints.delta_enforcer
    assert system_learning.constraints.delta_enforcer is not None