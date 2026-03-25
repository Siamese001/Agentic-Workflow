"""ADG-driven tests for apps_lic/tools/UpdateRecipientProfiles.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.UpdateRecipientProfiles  # noqa: F401


def test_module_importable():
    """Module UpdateRecipientProfiles must be importable."""
    assert apps_lic.tools.UpdateRecipientProfiles is not None
