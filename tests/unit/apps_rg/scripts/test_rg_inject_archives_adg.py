"""ADG-driven tests for apps_rg/scripts/rg_inject_archives.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.rg_inject_archives  # noqa: F401


def test_module_importable():
    """Module rg_inject_archives must be importable."""
    assert apps_rg.scripts.rg_inject_archives is not None
