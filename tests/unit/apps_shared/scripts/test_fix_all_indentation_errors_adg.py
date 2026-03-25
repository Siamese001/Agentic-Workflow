"""ADG-driven tests for apps_shared/scripts/fix_all_indentation_errors.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_all_indentation_errors  # noqa: F401


def test_module_importable():
    """Module fix_all_indentation_errors must be importable."""
    assert apps_shared.scripts.fix_all_indentation_errors is not None
