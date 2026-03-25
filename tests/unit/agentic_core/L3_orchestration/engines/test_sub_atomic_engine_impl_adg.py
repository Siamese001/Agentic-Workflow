"""ADG-driven tests for L3_orchestration/engines/sub_atomic_engine_impl.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.sub_atomic_engine_impl  # noqa: F401


def test_module_importable():
    """Module sub_atomic_engine_impl must be importable."""
    assert agentic_core.L3_orchestration.engines.sub_atomic_engine_impl is not None
