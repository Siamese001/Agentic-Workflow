"""ADG-driven tests for agentic_core/L5_safety/config/input_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.config.input_config  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.config.input_config  # noqa: F401
    """Module input_config must be importable."""
    assert agentic_core.L5_safety.config.input_config is not None
