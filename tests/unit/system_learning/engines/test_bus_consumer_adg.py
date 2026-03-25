"""ADG importability contract for system_learning/engines/bus_consumer.py."""
from __future__ import annotations

import system_learning.engines.bus_consumer  # noqa: F401


def test_module_importable():
    """Module bus_consumer must be importable."""
    assert system_learning.engines.bus_consumer is not None
