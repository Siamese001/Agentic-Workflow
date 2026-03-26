"""ADG-driven tests for agentic_core/L5_safety/config/blueprint_compiler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.config.blueprint_compiler  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.config.blueprint_compiler  # noqa: F401
        """Module blueprint_compiler must be importable."""
        assert agentic_core.L5_safety.config.blueprint_compiler is not None

    assert agentic_core.L5_safety.config.blueprint_compiler is not None
