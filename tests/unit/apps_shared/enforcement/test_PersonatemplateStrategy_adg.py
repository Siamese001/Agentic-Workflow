"""ADG-driven tests for apps_shared/enforcement/PersonatemplateStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.PersonatemplateStrategy  # noqa: F401


def test_module_importable():
    """Module PersonatemplateStrategy must be importable."""
    assert apps_shared.enforcement.PersonatemplateStrategy is not None
