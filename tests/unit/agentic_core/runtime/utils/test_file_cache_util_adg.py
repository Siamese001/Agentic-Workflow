"""ADG-driven tests for agentic_core/runtime/utils/file_cache_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.utils.file_cache_util  # noqa: F401


def test_module_importable():
    """Module file_cache_util must be importable."""
    assert agentic_core.runtime.utils.file_cache_util is not None
