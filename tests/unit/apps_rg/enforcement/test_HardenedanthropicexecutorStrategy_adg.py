"""ADG-driven tests for apps_rg/enforcement/HardenedanthropicexecutorStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.enforcement.HardenedanthropicexecutorStrategy  # noqa: F401


def test_module_importable():
    """Module HardenedanthropicexecutorStrategy must be importable."""
    assert apps_rg.enforcement.HardenedanthropicexecutorStrategy is not None
