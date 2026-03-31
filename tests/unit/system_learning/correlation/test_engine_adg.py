"""ADG importability contract for system_learning/correlation/engine.py."""
from __future__ import annotations

def test_module_importable():
    """Module engine must be importable."""
    import system_learning.correlation.engine
    assert system_learning.correlation.engine is not None
