"""ADG-driven tests for apps_lic/tools/GoogleSearchClient.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module GoogleSearchClient must be importable."""
    import apps_lic.tools.GoogleSearchClient  # noqa: F401

    assert apps_lic.tools.GoogleSearchClient is not None