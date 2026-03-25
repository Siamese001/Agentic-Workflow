"""ADG importability contract for system_learning/fingerprinting/engine.py."""
from __future__ import annotations

import system_learning.fingerprinting.engine  # noqa: F401


def test_module_importable():
    """Module engine must be importable."""
    assert system_learning.fingerprinting.engine is not None
