"""ADG-driven tests for apps_shared/scripts/fix_syntax_errors.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_syntax_errors  # noqa: F401


def test_module_importable():
    """Module fix_syntax_errors must be importable."""
    assert apps_shared.scripts.fix_syntax_errors is not None
