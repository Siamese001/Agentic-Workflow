"""ADG importability contract for system_learning/ports/outcome_write_back_hook.py."""
from __future__ import annotations



def test_module_importable():
    """Module outcome_write_back_hook must be importable."""
    import system_learning.ports.outcome_write_back_hook  # noqa: F401

    assert system_learning.ports.outcome_write_back_hook is not None
