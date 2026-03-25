"""ADG-driven tests for apps_lic/tools/SafetyProfile.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.SafetyProfile  # noqa: F401


def test_module_importable():
    """Module SafetyProfile must be importable."""
    assert apps_lic.tools.SafetyProfile is not None
