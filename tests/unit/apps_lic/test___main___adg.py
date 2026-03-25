"""ADG-driven tests for apps_lic/__main__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.__main__  # noqa: F401


def test_module_importable():
    """Module __main__ must be importable."""
    assert apps_lic.__main__ is not None
