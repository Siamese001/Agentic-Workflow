"""ADG-driven tests for apps_rg/scripts/test_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.test_engine  # noqa: F401


def test_module_importable():
    """Module test_engine must be importable."""
    assert apps_rg.scripts.test_engine is not None
