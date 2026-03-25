"""ADG-driven tests for apps_lic/tools/match_recipient_patterns.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.match_recipient_patterns  # noqa: F401


def test_module_importable():
    """Module match_recipient_patterns must be importable."""
    assert apps_lic.tools.match_recipient_patterns is not None
