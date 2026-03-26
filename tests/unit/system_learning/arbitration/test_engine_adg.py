"""ADG importability contract for system_learning/arbitration/engine.py."""
from __future__ import annotations

def test_module_importable():
    """Module engine must be importable."""
    import system_learning.arbitration.engine
    assert system_learning.arbitration.engine is not None