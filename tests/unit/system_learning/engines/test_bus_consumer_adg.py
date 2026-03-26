"""ADG importability contract for system_learning/engines/bus_consumer.py."""
from __future__ import annotations



def test_module_importable():
    """Module bus_consumer must be importable."""
    import system_learning.engines.bus_consumer  # noqa: F401

    assert system_learning.engines.bus_consumer is not None
