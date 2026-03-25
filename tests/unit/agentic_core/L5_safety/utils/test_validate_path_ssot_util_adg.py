"""ADG-driven tests for agentic_core/L5_safety/utils/validate_path_ssot_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.utils.validate_path_ssot_util  # noqa: F401


def test_module_importable():
    """Module validate_path_ssot_util must be importable."""
    assert agentic_core.L5_safety.utils.validate_path_ssot_util is not None
