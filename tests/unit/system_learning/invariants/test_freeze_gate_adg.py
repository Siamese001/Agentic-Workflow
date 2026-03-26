"""ADG importability contract for system_learning/invariants/freeze_gate.py."""
from __future__ import annotations



def test_module_importable():
    """Module freeze_gate must be importable."""
    import system_learning.invariants.freeze_gate  # noqa: F401

    assert system_learning.invariants.freeze_gate is not None
