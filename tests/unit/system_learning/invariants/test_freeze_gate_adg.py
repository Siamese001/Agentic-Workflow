"""ADG importability contract for system_learning/invariants/freeze_gate.py."""
from __future__ import annotations

import system_learning.invariants.freeze_gate  # noqa: F401


def test_module_importable():
    """Module freeze_gate must be importable."""
    assert system_learning.invariants.freeze_gate is not None
