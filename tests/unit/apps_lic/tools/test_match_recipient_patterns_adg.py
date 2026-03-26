"""ADG-driven tests for apps_lic/tools/match_recipient_patterns.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module match_recipient_patterns must be importable."""
    import apps_lic.tools.match_recipient_patterns  # noqa: F401

    assert apps_lic.tools.match_recipient_patterns is not None
