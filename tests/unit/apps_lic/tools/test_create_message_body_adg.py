"""ADG-driven tests for apps_lic/tools/create_message_body.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.create_message_body  # noqa: F401


def test_module_importable():
    """Module create_message_body must be importable."""
    assert apps_lic.tools.create_message_body is not None
