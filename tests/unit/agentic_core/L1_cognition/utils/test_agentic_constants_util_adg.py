"""ADG-driven tests for L1_cognition/utils/agentic_constants_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L1_cognition.utils.agentic_constants_util  # noqa: F401


def test_module_importable():
    """Module agentic_constants_util must be importable."""
    assert agentic_core.L1_cognition.utils.agentic_constants_util is not None
