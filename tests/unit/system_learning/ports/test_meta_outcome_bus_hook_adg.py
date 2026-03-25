"""ADG importability contract for system_learning/ports/meta_outcome_bus_hook.py."""
from __future__ import annotations

import system_learning.ports.meta_outcome_bus_hook  # noqa: F401


def test_module_importable():
    """Module meta_outcome_bus_hook must be importable."""
    assert system_learning.ports.meta_outcome_bus_hook is not None
