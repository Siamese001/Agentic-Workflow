"""ADG-driven tests for agentic_core/runtime/utils/dynamic_loader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.utils.dynamic_loader_util  # noqa: F401


def test_module_importable():
    """Module dynamic_loader_util must be importable."""
    assert agentic_core.runtime.utils.dynamic_loader_util is not None
