"""ADG-driven tests for apps_lic/tools/create_message_body.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module create_message_body must be importable."""
    import apps_lic.tools.create_message_body  # noqa: F401

    assert apps_lic.tools.create_message_body is not None
