"""ADG importability contract for system_learning/ports/meta_outcome_bus_hook.py."""
from __future__ import annotations

def test_module_importable():
    """Module meta_outcome_bus_hook must be importable."""
    import system_learning.ports.meta_outcome_bus_hook
    assert system_learning.ports.meta_outcome_bus_hook is not None