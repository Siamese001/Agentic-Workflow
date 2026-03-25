"""ADG-driven tests for apps_lic/tools/analyze_duplicates_detailed.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.analyze_duplicates_detailed  # noqa: F401


def test_module_importable():
    """Module analyze_duplicates_detailed must be importable."""
    assert apps_lic.tools.analyze_duplicates_detailed is not None
