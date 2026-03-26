"""ADG-driven tests for L5_safety/config/gravity_leak_config.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.config.gravity_leak_config  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.config.gravity_leak_config  # noqa: F401
    """Module gravity_leak_config must be importable."""
    assert agentic_core.L5_safety.config.gravity_leak_config is not None
