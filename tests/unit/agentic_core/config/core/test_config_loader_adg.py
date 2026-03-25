"""ADG-driven tests for agentic_core/config/core/config_loader.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.config_loader  # noqa: F401


def test_module_importable():
    """Module config_loader must be importable."""
    assert agentic_core.config.core.config_loader is not None
