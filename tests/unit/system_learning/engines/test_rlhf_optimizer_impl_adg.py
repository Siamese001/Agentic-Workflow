"""ADG-driven tests for system_learning/engines/rlhf_optimizer_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.rlhf_optimizer_impl  # noqa: F401


def test_module_importable():
    """Module rlhf_optimizer_impl must be importable."""
    assert system_learning.engines.rlhf_optimizer_impl is not None
