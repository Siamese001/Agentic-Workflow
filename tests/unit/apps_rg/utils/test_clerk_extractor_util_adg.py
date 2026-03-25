"""ADG-driven tests for apps_rg/utils/clerk_extractor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.utils.clerk_extractor_util  # noqa: F401


def test_module_importable():
    """Module clerk_extractor_util must be importable."""
    assert apps_rg.utils.clerk_extractor_util is not None
