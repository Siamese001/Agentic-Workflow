"""ADG-driven tests for apps_lic/tools/AdjustToneWeights.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module AdjustToneWeights must be importable."""
    import apps_lic.tools.AdjustToneWeights  # noqa: F401

    assert apps_lic.tools.AdjustToneWeights is not None