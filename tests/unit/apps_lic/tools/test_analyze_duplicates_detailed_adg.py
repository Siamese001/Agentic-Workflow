"""ADG-driven tests for apps_lic/tools/analyze_duplicates_detailed.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module analyze_duplicates_detailed must be importable."""
    import apps_lic.tools.analyze_duplicates_detailed  # noqa: F401

    assert apps_lic.tools.analyze_duplicates_detailed is not None
