"""ADG-driven tests for system_learning/adapters/live_run_pipeline_adapter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.adapters.live_run_pipeline_adapter  # noqa: F401


def test_module_importable():
    """Module live_run_pipeline_adapter must be importable."""
    assert system_learning.adapters.live_run_pipeline_adapter is not None
