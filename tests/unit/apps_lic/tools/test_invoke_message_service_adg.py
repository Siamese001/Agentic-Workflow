"""ADG-driven tests for apps_lic/tools/invoke_message_service.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.invoke_message_service  # noqa: F401


def test_module_importable():
    """Module invoke_message_service must be importable."""
    assert apps_lic.tools.invoke_message_service is not None
