"""ADG-driven tests for apps_shared/scripts/fix_all_violations.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_all_violations  # noqa: F401


def test_module_importable():
    """Module fix_all_violations must be importable."""
    assert apps_shared.scripts.fix_all_violations is not None
