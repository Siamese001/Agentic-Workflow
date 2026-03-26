"""ADG-driven tests for system_learning/engines/l3_efficiency_tuner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module l3_efficiency_tuner must be importable."""
    import system_learning.engines.l3_efficiency_tuner  # noqa: F401

    assert system_learning.engines.l3_efficiency_tuner is not None