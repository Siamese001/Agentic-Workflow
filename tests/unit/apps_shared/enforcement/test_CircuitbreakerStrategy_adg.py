"""ADG-driven tests for apps_shared/enforcement/CircuitbreakerStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.CircuitbreakerStrategy  # noqa: F401


def test_module_importable():
    """Module CircuitbreakerStrategy must be importable."""
    assert apps_shared.enforcement.CircuitbreakerStrategy is not None
