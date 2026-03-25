"""ADG-driven tests for apps_shared/types/multi_provider_clients.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.multi_provider_clients  # noqa: F401


def test_module_importable():
    """Module multi_provider_clients must be importable."""
    assert apps_shared.types.multi_provider_clients is not None
