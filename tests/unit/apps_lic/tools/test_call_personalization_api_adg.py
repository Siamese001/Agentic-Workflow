"""ADG-driven tests for apps_lic/tools/call_personalization_api.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.call_personalization_api  # noqa: F401


def test_module_importable():
    """Module call_personalization_api must be importable."""
    assert apps_lic.tools.call_personalization_api is not None
