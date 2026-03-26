"""ADG-driven tests for apps_lic/tools/InspectMessageQuality.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module InspectMessageQuality must be importable."""
    import apps_lic.tools.InspectMessageQuality  # noqa: F401

    assert apps_lic.tools.InspectMessageQuality is not None