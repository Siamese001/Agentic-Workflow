"""ADG-driven tests for system_learning/engines/signal_grouping_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module signal_grouping_engine must be importable."""
    import system_learning.engines.signal_grouping_engine  # noqa: F401

    assert system_learning.engines.signal_grouping_engine is not None