"""ADG-driven tests for apps_shared/enforcement/ReasoningrouterStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.ReasoningrouterStrategy  # noqa: F401


def test_module_importable():
    """Module ReasoningrouterStrategy must be importable."""
    assert apps_shared.enforcement.ReasoningrouterStrategy is not None
