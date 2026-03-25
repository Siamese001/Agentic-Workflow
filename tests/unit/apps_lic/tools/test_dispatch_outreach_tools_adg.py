"""ADG-driven tests for apps_lic/tools/dispatch_outreach_tools.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.dispatch_outreach_tools  # noqa: F401


def test_module_importable():
    """Module dispatch_outreach_tools must be importable."""
    assert apps_lic.tools.dispatch_outreach_tools is not None
