"""ADG-driven tests for config/core/env_loader.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.env_loader  # noqa: F401


def test_module_importable():
    """Module env_loader must be importable."""
    assert agentic_core.config.core.env_loader is not None
