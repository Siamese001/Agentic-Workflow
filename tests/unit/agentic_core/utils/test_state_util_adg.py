"""ADG-driven tests for utils/state_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.state_util  # noqa: F401


def test_module_importable():
    """Module state_util must be importable."""
    assert agentic_core.utils.state_util is not None
