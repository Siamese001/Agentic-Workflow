"""ADG-driven tests for apps_lic/tools/enforce_tone_guidelines.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.enforce_tone_guidelines  # noqa: F401


def test_module_importable():
    """Module enforce_tone_guidelines must be importable."""
    assert apps_lic.tools.enforce_tone_guidelines is not None
