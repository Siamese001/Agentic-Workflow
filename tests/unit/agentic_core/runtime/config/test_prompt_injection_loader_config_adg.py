"""ADG-driven tests for agentic_core/runtime/config/prompt_injection_loader_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.config.prompt_injection_loader_config  # noqa: F401


def test_module_importable():
    """Module prompt_injection_loader_config must be importable."""
    assert agentic_core.runtime.config.prompt_injection_loader_config is not None
