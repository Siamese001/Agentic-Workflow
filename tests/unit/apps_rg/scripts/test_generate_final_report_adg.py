"""ADG-driven tests for apps_rg/scripts/generate_final_report.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.generate_final_report  # noqa: F401


def test_module_importable():
    """Module generate_final_report must be importable."""
    assert apps_rg.scripts.generate_final_report is not None
