"""ADG-driven tests for apps_shared/scripts/clean_shims_simple.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.clean_shims_simple  # noqa: F401


def test_module_importable():
    """Module clean_shims_simple must be importable."""
    assert apps_shared.scripts.clean_shims_simple is not None
