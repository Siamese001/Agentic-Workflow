"""ADG-driven tests for apps_lic/tools/EvaluatePersonalizationQuality.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.EvaluatePersonalizationQuality  # noqa: F401


def test_module_importable():
    """Module EvaluatePersonalizationQuality must be importable."""
    assert apps_lic.tools.EvaluatePersonalizationQuality is not None
