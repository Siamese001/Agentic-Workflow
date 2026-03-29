"""ADG-driven tests for apps_rg/scripts/rg_inject_archives.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module rg_inject_archives must be importable."""
    import apps_rg.scripts.rg_inject_archives  # noqa: F401

    assert apps_rg.scripts.rg_inject_archives is not None
