"""ADG-driven tests for L2_execution/utils/deterministic_cleaner_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.utils.deterministic_cleaner_util  # noqa: F401


def test_module_importable():
    """Module deterministic_cleaner_util must be importable."""
    assert agentic_core.L2_execution.utils.deterministic_cleaner_util is not None
