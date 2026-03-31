"""ADG importability contract for system_learning/ports/__init__.py."""
from __future__ import annotations

def test_module_importable():
    """Module ports must be importable."""
    import system_learning.ports.__init__ as _mod
    assert _mod is not None
