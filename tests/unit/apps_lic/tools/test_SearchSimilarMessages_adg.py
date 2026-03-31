"""ADG-driven tests for apps_lic/tools/SearchSimilarMessages.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module SearchSimilarMessages must be importable."""
    import apps_lic.tools.SearchSimilarMessages  # noqa: F401

    assert apps_lic.tools.SearchSimilarMessages is not None
