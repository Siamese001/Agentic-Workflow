"""ADG-driven tests for apps_shared/scripts/handle_api_timeouts.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.handle_api_timeouts  # noqa: F401


def test_module_importable():
    """Module handle_api_timeouts must be importable."""
    assert apps_shared.scripts.handle_api_timeouts is not None
