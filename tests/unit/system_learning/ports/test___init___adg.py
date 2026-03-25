"""ADG importability contract for system_learning/ports/__init__.py."""
from __future__ import annotations

import system_learning.ports.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module ports must be importable."""
    assert _mod is not None
