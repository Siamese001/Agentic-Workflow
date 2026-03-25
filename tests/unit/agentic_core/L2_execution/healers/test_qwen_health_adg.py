"""ADG-driven tests for agentic_core/L2_execution/healers/qwen_health.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.healers.qwen_health  # noqa: F401


def test_module_importable():
    """Module qwen_health must be importable."""
    assert agentic_core.L2_execution.healers.qwen_health is not None
