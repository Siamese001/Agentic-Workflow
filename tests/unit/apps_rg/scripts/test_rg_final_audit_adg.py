"""ADG-driven tests for apps_rg/scripts/rg_final_audit.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.rg_final_audit  # noqa: F401


def test_module_importable():
    """Module rg_final_audit must be importable."""
    assert apps_rg.scripts.rg_final_audit is not None
