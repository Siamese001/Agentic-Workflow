"""ADG-driven tests for apps_rg/tools/invoke_generation_service.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.invoke_generation_service  # noqa: F401


def test_module_importable():
    """Module invoke_generation_service must be importable."""
    assert apps_rg.tools.invoke_generation_service is not None
