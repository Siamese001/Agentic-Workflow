"""ADG-driven tests for apps_lic/tools/clean_duplicates_enhanced.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.clean_duplicates_enhanced  # noqa: F401


def test_module_importable():
    """Module clean_duplicates_enhanced must be importable."""
    assert apps_lic.tools.clean_duplicates_enhanced is not None
