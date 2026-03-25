"""ADG-driven tests for agentic_core/config/core/domain_constitution_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.domain_constitution_config  # noqa: F401


def test_module_importable():
    """Module domain_constitution_config must be importable."""
    assert agentic_core.config.core.domain_constitution_config is not None
