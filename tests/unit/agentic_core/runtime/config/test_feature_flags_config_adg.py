"""ADG-driven tests for agentic_core/runtime/config/feature_flags_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.config.feature_flags_config  # noqa: F401


def test_module_importable():
    """Module feature_flags_config must be importable."""
    assert agentic_core.runtime.config.feature_flags_config is not None
