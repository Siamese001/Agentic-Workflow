"""ADG-driven tests for agentic_core/runtime/utils/main_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.utils.main_util  # noqa: F401


def test_module_importable():
    """Module main_util must be importable."""
    assert agentic_core.runtime.utils.main_util is not None
