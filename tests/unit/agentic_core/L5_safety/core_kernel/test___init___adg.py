"""ADG-driven tests for agentic_core/L5_safety/core_kernel/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.core_kernel.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module core_kernel must be importable."""
    assert _mod is not None
