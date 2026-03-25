"""ADG-driven tests for agentic_core/config/core/complexity_metrics_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.complexity_metrics_config  # noqa: F401


def test_module_importable():
    """Module complexity_metrics_config must be importable."""
    assert agentic_core.config.core.complexity_metrics_config is not None
