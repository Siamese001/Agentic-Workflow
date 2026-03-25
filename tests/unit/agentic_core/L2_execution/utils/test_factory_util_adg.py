"""ADG-driven tests for agentic_core/L2_execution/utils/factory_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.utils.factory_util  # noqa: F401


def test_module_importable():
    """Module factory_util must be importable."""
    assert agentic_core.L2_execution.utils.factory_util is not None
