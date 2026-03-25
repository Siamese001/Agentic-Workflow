"""ADG-driven tests for apps_lic/engines/message_body_composer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.engines.message_body_composer as _mod  # noqa: F401


def test_module_importable():
    """Module message_body_composer must be importable."""
    assert _mod is not None
