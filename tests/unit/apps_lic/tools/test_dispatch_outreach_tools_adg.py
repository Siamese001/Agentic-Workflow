"""ADG-driven tests for apps_lic/tools/dispatch_outreach_tools.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module dispatch_outreach_tools must be importable."""
    import apps_lic.tools.dispatch_outreach_tools  # noqa: F401

    assert apps_lic.tools.dispatch_outreach_tools is not None
