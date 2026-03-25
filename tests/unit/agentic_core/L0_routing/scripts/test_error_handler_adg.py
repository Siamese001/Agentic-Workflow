"""ADG-driven tests for agentic_core/L0_routing/scripts/error_handler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.error_handler  # noqa: F401


def test_module_importable():
    """Module error_handler must be importable."""
    assert agentic_core.L0_routing.scripts.error_handler is not None
