"""ADG-driven tests for agentic_core/runtime/config/injection_type_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.config.injection_type_config  # noqa: F401


def test_module_importable():
    """Module injection_type_config must be importable."""
    assert agentic_core.runtime.config.injection_type_config is not None
