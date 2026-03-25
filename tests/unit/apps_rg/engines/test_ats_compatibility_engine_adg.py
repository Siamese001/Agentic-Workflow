"""ADG-driven tests for apps_rg/engines/ats_compatibility_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.ats_compatibility_engine  # noqa: F401


def test_module_importable():
    """Module ats_compatibility_engine must be importable."""
    assert apps_rg.engines.ats_compatibility_engine is not None
