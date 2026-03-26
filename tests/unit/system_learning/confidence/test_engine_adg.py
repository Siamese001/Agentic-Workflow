"""ADG importability contract for system_learning/confidence/engine.py."""
from __future__ import annotations

def test_module_importable():
    """Module engine must be importable."""
    import system_learning.confidence.engine
    assert system_learning.confidence.engine is not None