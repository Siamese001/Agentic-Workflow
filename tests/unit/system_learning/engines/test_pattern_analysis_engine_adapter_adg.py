"""ADG-driven tests for system_learning/engines/pattern_analysis_engine_adapter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.pattern_analysis_engine_adapter  # noqa: F401


def test_module_importable():
    """Module pattern_analysis_engine_adapter must be importable."""
    assert system_learning.engines.pattern_analysis_engine_adapter is not None
