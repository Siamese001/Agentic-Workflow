"""ADG-driven tests for system_learning/engines/rlhf_optimizer_impl.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module rlhf_optimizer_impl must be importable."""
    import system_learning.engines.rlhf_optimizer_impl
    assert system_learning.engines.rlhf_optimizer_impl is not None