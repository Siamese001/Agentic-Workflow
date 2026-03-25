"""ADG-driven tests for apps_lic/tools/GoogleSearchClient.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.GoogleSearchClient  # noqa: F401


def test_module_importable():
    """Module GoogleSearchClient must be importable."""
    assert apps_lic.tools.GoogleSearchClient is not None
