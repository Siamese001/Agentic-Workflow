"""ADG-driven tests for apps_lic/tools/query_past_campaigns.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module query_past_campaigns must be importable."""
    import apps_lic.tools.query_past_campaigns  # noqa: F401

    assert apps_lic.tools.query_past_campaigns is not None