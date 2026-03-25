"""ADG-driven tests for apps_lic/tools/AssessContentRisk.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.AssessContentRisk  # noqa: F401


def test_module_importable():
    """Module AssessContentRisk must be importable."""
    assert apps_lic.tools.AssessContentRisk is not None
