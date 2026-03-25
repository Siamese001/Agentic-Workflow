"""ADG-driven tests for agentic_core/L5_safety/utils/validation_utils_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.utils.validation_utils_util  # noqa: F401


def test_module_importable():
    """Module validation_utils_util must be importable."""
    assert agentic_core.L5_safety.utils.validation_utils_util is not None
