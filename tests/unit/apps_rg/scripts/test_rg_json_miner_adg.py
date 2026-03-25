"""ADG-driven tests for apps_rg/scripts/rg_json_miner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.rg_json_miner  # noqa: F401


def test_module_importable():
    """Module rg_json_miner must be importable."""
    assert apps_rg.scripts.rg_json_miner is not None
