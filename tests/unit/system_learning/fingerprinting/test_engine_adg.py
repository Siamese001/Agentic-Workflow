"""ADG importability contract for system_learning/fingerprinting/engine.py."""
from __future__ import annotations

def test_module_importable():
    """Module engine must be importable."""
    import system_learning.fingerprinting.engine
    assert system_learning.fingerprinting.engine is not None
