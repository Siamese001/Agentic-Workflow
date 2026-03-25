"""ADG importability contract for system_learning/engines/in_memory_healing_outcome_intake_store.py."""
from __future__ import annotations

import system_learning.engines.in_memory_healing_outcome_intake_store  # noqa: F401


def test_module_importable():
    """Module in_memory_healing_outcome_intake_store must be importable."""
    assert system_learning.engines.in_memory_healing_outcome_intake_store is not None
